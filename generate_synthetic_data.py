#!/usr/bin/env python3
"""
Synthetic Participant Data Generation Pipeline
Generates N synthetic participants via multiple LLMs playing the role of junior employees
providing feedback through the chatbot study flow.

Thesis methodology: Sections 3.7 and 5.6
Supervisor-approved supplement to human sample for statistical power.
"""

import json
import os
import csv
import random
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple
import anthropic
import openai
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv('backend/.env')

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(output_dir: str) -> logging.Logger:
    """Configure detailed logging to both console and file."""
    log_file = f"{output_dir}/generation.log"

    logger = logging.getLogger("SyntheticDataGen")
    logger.setLevel(logging.DEBUG)

    # File handler (detailed)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(fh)

    # Console handler (info and above)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(ch)

    return logger

# ============================================================================
# CONFIG & SETUP
# ============================================================================

def load_config(config_path: str = "synthetic_data_config.json") -> Dict:
    """Load configuration file."""
    with open(config_path) as f:
        return json.load(f)

def setup_output_dirs(config: Dict):
    """Create output directories."""
    out_dir = config["output"]["directory"]
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/{config['output']['files']['transcripts_dir']}", exist_ok=True)
    return out_dir

# ============================================================================
# PARTICIPANT ASSIGNMENT & ALLOCATION
# ============================================================================

def create_participant_allocation(
    config: Dict,
    seed: Optional[int] = None,
    model_filter: Optional[str] = None,
) -> List[Dict]:
    """
    Create balanced allocation of participants across conditions and models.
    Returns list of dicts: {participant_id, condition, model_id, model_name, provider}

    model_filter: if given, restrict generation to models whose display_name
    contains this substring (case-insensitive), e.g. "sonnet".
    """
    if seed is not None:
        random.seed(seed)

    participants = []
    models = config["models"]
    conditions = config["target"]["conditions"]
    per_condition = config["target"]["per_condition"]

    if model_filter:
        models = [m for m in models if model_filter.lower() in m["display_name"].lower()]
        if not models:
            raise ValueError(f"No models match filter '{model_filter}'")

    # For each condition, create equal distribution across models
    for condition in conditions:
        for model_config in models:
            count = model_config.get("allocation_per_condition", per_condition // len(models))
            for _ in range(count):
                participants.append({
                    "participant_id": str(uuid.uuid4()),
                    "condition": condition,
                    "model_id": model_config["model_id"],
                    "model_name": model_config["display_name"],
                    "provider": model_config["provider"],
                    "api_key_env": model_config["api_key_env"],
                })

    random.shuffle(participants)
    return participants

# ============================================================================
# DEMOGRAPHICS GENERATION
# ============================================================================

def generate_random_demographics(config: Dict) -> Dict:
    """Generate plausible random demographics for synthetic participant."""
    demo = config["demographics"]

    return {
        "age": random.randint(demo["age_range"][0], demo["age_range"][1]),
        "gender": random.choice(demo["genders"]),
        "industry": random.choice(demo["industries"]),
        "job_role": random.choice(demo["job_roles"]),
        "years_work_experience": round(random.uniform(demo["work_experience_range"][0],
                                                       demo["work_experience_range"][1]), 1),
        "ai_experience": random.randint(demo["ai_experience_range"][0],
                                       demo["ai_experience_range"][1]),
    }

# ============================================================================
# LLM PARTICIPANT ROLE CALLS
# ============================================================================

def call_claude_participant(
    model_id: str,
    vignette: str,
    conversation_history: List[Dict],
    api_key: str,
    max_tokens: int = 500,
) -> str:
    """Call Claude API as participant LLM."""
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = f"""You are a junior employee or intern in a team. Your role:

{vignette}

Respond naturally and authentically as this character would. Be specific and constructive.
Keep responses reasonably concise (1-3 paragraphs per turn).
Answer the assistant's questions directly and thoughtfully."""

    messages = conversation_history.copy()

    # Ensure messages array is not empty
    if not messages:
        raise ValueError("conversation_history cannot be empty for Claude API call")

    response = client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )

    # Handle extended thinking (find TextBlock, skip ThinkingBlock)
    for block in response.content:
        if hasattr(block, 'text'):
            return block.text

    raise ValueError("No text block found in Claude response")


def call_openai_participant(
    model_id: str,
    vignette: str,
    conversation_history: List[Dict],
    api_key: str,
    max_tokens: int = 500,
) -> str:
    """Call OpenAI API as participant LLM."""
    client = openai.OpenAI(api_key=api_key)

    system_prompt = f"""You are a junior employee or intern in a team. Your role:

{vignette}

Respond naturally and authentically as this character would. Be specific and constructive.
Keep responses reasonably concise (1-3 paragraphs per turn).
Answer the assistant's questions directly and thoughtfully."""

    messages = [{"role": "system", "content": system_prompt}] + conversation_history

    response = client.chat.completions.create(
        model=model_id,
        max_tokens=max_tokens,
        messages=messages,
    )

    return response.choices[0].message.content


def get_participant_response(
    provider: str,
    model_id: str,
    vignette: str,
    conversation_history: List[Dict],
    api_key: str,
) -> str:
    """Route to appropriate LLM provider."""
    if provider == "anthropic":
        return call_claude_participant(model_id, vignette, conversation_history, api_key)
    elif provider == "openai":
        return call_openai_participant(model_id, vignette, conversation_history, api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")

# ============================================================================
# CHATBOT BACKEND CALLS
# ============================================================================

def init_participant_session(
    condition: str,
    backend_url: str,
    admin_token: str,
) -> Tuple[str, bool]:
    """
    Initialize a participant session on the backend.
    Returns: (participant_id, success) - participant_id from backend or None if failed
    """
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        payload = {
            "consented": True,
            "forced_condition": condition,
        }

        response = requests.post(
            f"{backend_url}/session/start",
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            backend_participant_id = data.get("participant_id")
            return backend_participant_id, True
        else:
            print(f"⚠ Failed to init session: {response.status_code}")
            return None, False
    except Exception as e:
        print(f"⚠ Failed to init session: {e}")
        return None, False


def call_chatbot_backend(
    condition: str,
    participant_id: str,
    user_message: str,
    turn_index: int,
    backend_url: str,
    admin_token: str,
) -> Tuple[str, bool]:
    """
    Call the FastAPI backend chatbot endpoint.
    Returns: (chatbot_response, success)
    """
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Backend only expects participant_id and message
        payload = {
            "participant_id": participant_id,
            "message": user_message,
        }

        response = requests.post(
            f"{backend_url}/chat",
            json=payload,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            # Extract assistant message from the response
            assistant_data = data.get("assistant_message", {})
            if isinstance(assistant_data, dict):
                assistant_message = assistant_data.get("content", "")
            else:
                assistant_message = str(assistant_data)
            return assistant_message, True
        else:
            print(f"⚠ Backend error {response.status_code} for participant {participant_id}: {response.text}")
            return "", False
    except Exception as e:
        print(f"⚠ Failed to call backend: {e}")
        return "", False

# ============================================================================
# CONVERSATION FLOW
# ============================================================================

def run_synthetic_session(
    participant: Dict,
    config: Dict,
) -> Dict:
    """
    Run one complete synthetic participant session.
    Returns session data: transcript, metrics, completion status.
    """
    condition = participant["condition"]
    model_id = participant["model_id"]
    provider = participant["provider"]
    api_key_env = participant["api_key_env"]

    # Get API key
    api_key = os.getenv(api_key_env)
    if not api_key:
        print(f"[FAIL] Missing API key env var: {api_key_env}")
        return None

    backend_url = config["chatbot"]["backend_url"]
    admin_token = config["chatbot"]["admin_token"]
    prompts = config["chatbot"]["prompts"]
    vignette = config["vignette"]["text"]

    # Initialize participant on backend (this generates the participant_id)
    participant_id, init_success = init_participant_session(condition, backend_url, admin_token)
    if not init_success or not participant_id:
        return {
            "participant_id": participant_id,
            "condition": condition,
            "model_name": participant.get("model_name", "Unknown"),
            "model_id": model_id,
            "provider": provider,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "transcript": [],
            "total_turns": 0,
            "total_user_words": 0,
            "total_assistant_words": 0,
            "average_user_message_length": 0,
            "completed_task": False,
            "dropout_stage": "init_session_failed",
            "demographics": generate_random_demographics(config),
        }

    # Initialize session
    session_data = {
        "participant_id": participant_id,
        "condition": condition,
        "model_name": participant["model_name"],
        "model_id": model_id,
        "provider": provider,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "transcript": [],
        "total_turns": 0,
        "total_user_words": 0,
        "total_assistant_words": 0,
        "average_user_message_length": 0,
        "completed_task": False,
        "dropout_stage": None,
        "demographics": generate_random_demographics(config),
    }

    # Conversation loop
    conversation_history = []
    turn_index = 0

    for prompt_idx, chatbot_prompt in enumerate(prompts):
        turn_index = prompt_idx

        # Add chatbot prompt to conversation FIRST
        conversation_history.append({
            "role": "user",
            "content": chatbot_prompt,
        })

        # Call participant LLM with the prompt in context
        try:
            participant_response = get_participant_response(
                provider=provider,
                model_id=model_id,
                vignette=vignette,
                conversation_history=conversation_history,
                api_key=api_key,
            )
        except Exception as e:
            print(f"[FAIL] Participant LLM error for {participant_id}: {e}")
            session_data["dropout_stage"] = f"turn_{turn_index}_participant_error"
            return session_data

        # Add participant response to conversation
        conversation_history.append({
            "role": "assistant",
            "content": participant_response,
        })

        # Call chatbot backend
        assistant_response, success = call_chatbot_backend(
            condition=condition,
            participant_id=participant_id,
            user_message=participant_response,
            turn_index=turn_index,
            backend_url=backend_url,
            admin_token=admin_token,
        )

        if not success:
            session_data["dropout_stage"] = f"turn_{turn_index}_backend_error"
            return session_data

        # Record in transcript
        session_data["transcript"].append({
            "turn_index": turn_index,
            "chatbot_prompt": chatbot_prompt,
            "participant_response": participant_response,
            "assistant_followup": assistant_response,
        })

        # Track metrics
        session_data["total_turns"] += 1
        participant_words = len(participant_response.split())
        session_data["total_user_words"] += participant_words
        assistant_words = len(assistant_response.split())
        session_data["total_assistant_words"] += assistant_words

    # Calculate average message length
    if session_data["total_turns"] > 0:
        session_data["average_user_message_length"] = round(
            session_data["total_user_words"] / session_data["total_turns"], 2
        )

    session_data["completed_task"] = True
    session_data["completed_at"] = datetime.utcnow().isoformat()

    return session_data

# ============================================================================
# QUESTIONNAIRE GENERATION
# ============================================================================

def generate_questionnaire_response(
    session_data: Dict,
    config: Dict,
    participant_model: str,
    provider: str,
    api_key: str,
) -> Dict:
    """
    Generate questionnaire responses from participant LLM.
    Must output structured JSON matching questionnaires.csv schema.
    """
    if not session_data["completed_task"]:
        return None  # No questionnaire if task incomplete

    condition = session_data["condition"]
    transcript_text = json.dumps(session_data["transcript"], indent=2)

    questionnaire_prompt = f"""Based on your conversation above, please answer these questions about your experience.
For each question, provide a numeric response on the given scale.

Respond ONLY with a valid JSON object, no additional text. Use these exact field names:
- perc_warmth_bipolar: 1-7 scale (1=Warm/supportive, 7=Direct/formal)
- perc_task_focus_bipolar: 1-7 scale (1=Comforting, 7=Task-focused)
- psych_safe_1: 1-7 scale (I felt safe to express concerns)
- psych_safe_2: 1-7 scale (I could be honest without fear)
- psych_safe_3: 1-7 scale (I felt comfortable sharing critical feedback)
- openness_1: 1-7 scale (I answered honestly)
- openness_2_raw: 1-7 scale (I held back my true thoughts - raw score, will be reverse-coded)
- engagement_self_report: 1-7 scale (I felt engaged)

Example output:
{{"perc_warmth_bipolar": 3, "perc_task_focus_bipolar": 5, "psych_safe_1": 6, "psych_safe_2": 5, "psych_safe_3": 6, "openness_1": 6, "openness_2_raw": 2, "engagement_self_report": 5}}

Your conversation transcript:
{transcript_text}

Now provide your responses as JSON only:"""

    try:
        if provider == "anthropic":
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=participant_model,
                max_tokens=300,
                messages=[{"role": "user", "content": questionnaire_prompt}],
            )
            response_text = response.content[0].text
        else:  # openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=participant_model,
                max_tokens=300,
                messages=[{"role": "user", "content": questionnaire_prompt}],
            )
            response_text = response.choices[0].message.content

        # Extract JSON from response (handle markdown code fences)
        response_text = response_text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()

        # Parse JSON
        questionnaire_data = json.loads(response_text)

        # Add computed means
        psych_safe_scores = [
            questionnaire_data.get("psych_safe_1", 0),
            questionnaire_data.get("psych_safe_2", 0),
            questionnaire_data.get("psych_safe_3", 0),
        ]
        questionnaire_data["psychological_safety_mean"] = round(
            sum(psych_safe_scores) / len(psych_safe_scores), 2
        )

        openness_scores = [
            questionnaire_data.get("openness_1", 0),
            7 - questionnaire_data.get("openness_2_raw", 0),  # reverse coded
        ]
        questionnaire_data["self_reported_honesty_mean"] = round(
            sum(openness_scores) / len(openness_scores), 2
        )

        return questionnaire_data

    except json.JSONDecodeError as e:
        print(f"[FAIL] Failed to parse questionnaire JSON: {e}")
        return None
    except Exception as e:
        print(f"[FAIL] Questionnaire generation error: {e}")
        return None

# ============================================================================
# OUTPUT WRITING
# ============================================================================

def write_participants_csv(sessions: List[Dict], output_dir: str):
    """Write participants.csv file. Appends to existing file rather than overwriting."""
    csv_path = f"{output_dir}/synthetic_participants.csv"
    file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0

    with open(csv_path, "a" if file_exists else "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "participant_id",
            "condition",
            "model_name",
            "model_id",
            "completed_task",
            "number_user_turns",
            "total_user_word_count",
            "average_user_message_length",
            "started_at",
            "completed_at",
            "dropout_stage",
        ])
        if not file_exists:
            writer.writeheader()

        for session in sessions:
            writer.writerow({
                "participant_id": session["participant_id"],
                "condition": session["condition"],
                "model_name": session["model_name"],
                "model_id": session["model_id"],
                "completed_task": int(session["completed_task"]),
                "number_user_turns": session["total_turns"],
                "total_user_word_count": session["total_user_words"],
                "average_user_message_length": session["average_user_message_length"],
                "started_at": session["started_at"],
                "completed_at": session["completed_at"],
                "dropout_stage": session["dropout_stage"] or "",
            })

    print(f"[OK] Wrote {csv_path}")


def write_questionnaires_csv(
    sessions: List[Dict],
    questionnaires: Dict[str, Dict],
    output_dir: str,
):
    """Write questionnaires.csv file. Appends to existing file rather than overwriting."""
    csv_path = f"{output_dir}/synthetic_questionnaires.csv"
    file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0

    with open(csv_path, "a" if file_exists else "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "participant_id",
            "condition",
            "model_name",
            "model_id",
            "perc_warmth_bipolar",
            "perc_task_focus_bipolar",
            "psych_safe_1",
            "psych_safe_2",
            "psych_safe_3",
            "psychological_safety_mean",
            "openness_1",
            "openness_2_raw",
            "self_reported_honesty_mean",
            "engagement_self_report",
            "ai_experience",
            "years_work_experience",
            "age",
            "gender",
            "industry",
            "job_role",
            "timestamp_submit",
        ])
        if not file_exists:
            writer.writeheader()

        for session in sessions:
            participant_id = session["participant_id"]
            if participant_id not in questionnaires:
                continue

            q = questionnaires[participant_id]
            writer.writerow({
                "participant_id": participant_id,
                "condition": session["condition"],
                "model_name": session["model_name"],
                "model_id": session["model_id"],
                "perc_warmth_bipolar": q.get("perc_warmth_bipolar", ""),
                "perc_task_focus_bipolar": q.get("perc_task_focus_bipolar", ""),
                "psych_safe_1": q.get("psych_safe_1", ""),
                "psych_safe_2": q.get("psych_safe_2", ""),
                "psych_safe_3": q.get("psych_safe_3", ""),
                "psychological_safety_mean": q.get("psychological_safety_mean", ""),
                "openness_1": q.get("openness_1", ""),
                "openness_2_raw": q.get("openness_2_raw", ""),
                "self_reported_honesty_mean": q.get("self_reported_honesty_mean", ""),
                "engagement_self_report": q.get("engagement_self_report", ""),
                "ai_experience": session["demographics"]["ai_experience"],
                "years_work_experience": session["demographics"]["years_work_experience"],
                "age": session["demographics"]["age"],
                "gender": session["demographics"]["gender"],
                "industry": session["demographics"]["industry"],
                "job_role": session["demographics"]["job_role"],
                "timestamp_submit": session["completed_at"],
            })

    print(f"[OK] Wrote {csv_path}")


def save_transcript_json(session: Dict, output_dir: str):
    """Save individual transcript to JSON for honesty coding."""
    if not session["completed_task"]:
        return

    transcript_path = f"{output_dir}/transcripts/{session['participant_id']}.json"

    with open(transcript_path, "w") as f:
        json.dump({
            "participant_id": session["participant_id"],
            "condition": session["condition"],
            "model_name": session["model_name"],
            "transcript": session["transcript"],
        }, f, indent=2)


def write_procedure_log(
    config: Dict,
    allocation: List[Dict],
    sessions: List[Dict],
    output_dir: str,
):
    """Document the generation procedure for reproducibility."""
    log_path = f"{output_dir}/generation_procedure.json"

    completed_count = sum(1 for s in sessions if s["completed_task"])

    log = {
        "timestamp_generated": datetime.utcnow().isoformat(),
        "thesis_reference": "Sections 3.7 and 5.6 - Synthetic Sample Methodology",
        "config_used": config,
        "total_participants_requested": config["target"]["total_participants"],
        "total_participants_completed": completed_count,
        "completion_rate": round(completed_count / len(sessions), 2),
        "models_used": [m["display_name"] for m in config["models"]],
        "conditions_balanced": {
            "warm": sum(1 for s in sessions if s["condition"] == "warm" and s["completed_task"]),
            "competent": sum(1 for s in sessions if s["condition"] == "competent" and s["completed_task"]),
        },
        "model_distribution": {
            model: {
                condition: sum(
                    1 for s in sessions
                    if s["model_name"] == model
                    and s["condition"] == condition
                    and s["completed_task"]
                )
                for condition in ["warm", "competent"]
            }
            for model in [m["display_name"] for m in config["models"]]
        },
    }

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    print(f"[OK] Wrote {log_path}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic participant data")
    parser.add_argument(
        "--model",
        default=None,
        help="Restrict generation to models whose display_name contains this "
             "substring (case-insensitive), e.g. --model sonnet. Omit to run all models.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Setup
    config = load_config()
    output_dir = setup_output_dirs(config)
    logger = setup_logging(output_dir)

    logger.info("=" * 70)
    logger.info("Synthetic Participant Data Generation Pipeline")
    logger.info("Thesis Methodology: Sections 3.7 and 5.6")
    logger.info("=" * 70)

    # Windows console fix for Unicode
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Log file: {output_dir}/generation.log")

    # Load config
    try:
        logger.debug(f"Loading config from synthetic_data_config.json")
        logger.info(f"[OK] Config loaded")
        logger.info(f"[OK] Target: {config['target']['total_participants']} participants "
                   f"({config['target']['per_condition']} per condition)")
        if args.model:
            logger.info(f"[OK] Model filter active: only models matching '{args.model}'")
        logger.info(f"[OK] Models: {', '.join(m['display_name'] for m in config['models'])}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # Create allocation
    try:
        logger.info(f"\n[*] Creating participant allocation...")
        allocation = create_participant_allocation(config, seed=42, model_filter=args.model)
        logger.info(f"[OK] Created {len(allocation)} balanced allocations")
        logger.debug(f"  Warm: {sum(1 for a in allocation if a['condition']=='warm')}")
        logger.debug(f"  Competent: {sum(1 for a in allocation if a['condition']=='competent')}")
        for model in config['models']:
            count = sum(1 for a in allocation if a['model_id']==model['model_id'])
            logger.debug(f"  {model['display_name']}: {count}")
    except Exception as e:
        logger.error(f"Failed to create allocation: {e}")
        return

    # Run sessions
    logger.info(f"\n[*] Running {len(allocation)} synthetic sessions...")
    logger.info(f"(This will take 30-45 minutes. Progress logged below.)\n")

    sessions = []
    questionnaires = {}
    failed_sessions = []
    failed_questionnaires = []

    for idx, participant_config in enumerate(allocation, 1):
        participant_id = participant_config["participant_id"]
        model_name = participant_config["model_name"]
        condition = participant_config["condition"]

        status_msg = f"[{idx:3d}/{len(allocation)}] {model_name:15s} ({condition:10s}) | {participant_id[:12]}..."
        logger.info(status_msg)

        # Run session
        session = run_synthetic_session(participant_config, config)
        if session is None:
            logger.warning("[FAIL] Session initialization failed")
            failed_sessions.append(participant_id)
            continue

        sessions.append(session)

        # Generate questionnaire
        if session["completed_task"]:
            api_key = os.getenv(participant_config["api_key_env"])
            q_response = generate_questionnaire_response(
                session,
                config,
                participant_config["model_id"],
                participant_config["provider"],
                api_key,
            )

            if q_response:
                questionnaires[session["participant_id"]] = q_response
                engagement = q_response.get('engagement_self_report', '?')
                psych_safe = q_response.get('psychological_safety_mean', '?')
                logger.info(f"[OK] H={engagement}, PS={psych_safe}")
            else:
                logger.warning(f"[WARN] Session OK, questionnaire failed")
                failed_questionnaires.append(participant_id)
                session["dropout_stage"] = "questionnaire_generation_error"

            # Save transcript
            save_transcript_json(session, output_dir)
        else:
            logger.warning(f"[FAIL] Dropout: {session['dropout_stage']}")
            failed_sessions.append(participant_id)

    # Write outputs
    logger.info(f"\n[*] Writing outputs...")
    try:
        write_participants_csv(sessions, output_dir)
        write_questionnaires_csv(sessions, questionnaires, output_dir)
        write_procedure_log(config, allocation, sessions, output_dir)
        logger.info(f"[OK] All outputs written successfully")
    except Exception as e:
        logger.error(f"Failed to write outputs: {e}")
        return

    # Summary
    completed = sum(1 for s in sessions if s["completed_task"])
    warm_complete = sum(1 for s in sessions if s['condition']=='warm' and s['completed_task'])
    competent_complete = sum(1 for s in sessions if s['condition']=='competent' and s['completed_task'])
    completion_rate = round(100 * completed / len(sessions), 1)

    logger.info(f"\n" + "=" * 70)
    logger.info(f"[OK] GENERATION COMPLETE")
    logger.info(f"=" * 70)
    logger.info(f"Sessions completed: {completed}/{len(sessions)} ({completion_rate}%)")
    logger.info(f"  - Warm condition: {warm_complete}/50")
    logger.info(f"  - Competent condition: {competent_complete}/50")
    logger.info(f"  - Balance: {warm_complete}W / {competent_complete}C")
    logger.info(f"\nQuestionnaires:")
    logger.info(f"  - Completed: {len(questionnaires)}")
    if failed_questionnaires:
        logger.warning(f"  - Failed: {len(failed_questionnaires)}")

    if failed_sessions:
        logger.warning(f"\nDropouts: {len(failed_sessions)} participants")
        logger.debug(f"  IDs: {failed_sessions}")

    logger.info(f"\nOutput files in {output_dir}:")
    logger.info(f"  [OK] synthetic_participants.csv ({len(sessions)} rows)")
    logger.info(f"  [OK] synthetic_questionnaires.csv ({len(questionnaires)} rows)")
    logger.info(f"  [OK] transcripts/ ({len([s for s in sessions if s['completed_task']])} JSON files)")
    logger.info(f"  [OK] generation.log (this log)")
    logger.info(f"  [OK] generation_procedure.json (reproducibility)")
    logger.info(f"\nNext step: python code_transcript_honesty.py")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
