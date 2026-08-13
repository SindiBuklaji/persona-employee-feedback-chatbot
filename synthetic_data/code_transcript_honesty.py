#!/usr/bin/env python3
"""
Honesty Coding Agent
Applies Appendix G rubric to synthetic participant transcripts independently.
Decoupled from participant-generation LLM to minimize response bias.
"""

import json
import os
import csv
import glob
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
import anthropic
from dotenv import load_dotenv

# Load .env file
load_dotenv('backend/.env')

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = logging.getLogger("HonestyCoder")

def setup_logging(output_dir: str) -> logging.Logger:
    """Configure detailed logging to both console and file."""
    log_file = f"{output_dir}/honesty_coding.log"

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
# CONFIG
# ============================================================================

HONESTY_RUBRIC = {
    "criticality": {
        "scale": [0, 3],
        "definition": "Intensity and weight of the problem evaluation",
        "anchors": [
            "0 = Surface-level observation, minimal problem severity",
            "1 = Mild acknowledgment of issues",
            "2 = Moderate critique of practices",
            "3 = Intense, direct critique of fundamental team failures",
        ]
    },
    "specificity": {
        "scale": [0, 3],
        "definition": "Concrete detail and contextual grounding vs. vague statements",
        "anchors": [
            "0 = Generic complaint, no specific examples",
            "1 = Vague reference to issues",
            "2 = Some concrete examples but abstract reasoning",
            "3 = Detailed, concrete examples with clear context and impact",
        ]
    },
    "riskiness": {
        "scale": [0, 3],
        "definition": "Degree to which feedback challenges established authority/practices",
        "anchors": [
            "0 = Affirms status quo, no challenge",
            "1 = Minor critique of processes",
            "2 = Moderate challenge to practices",
            "3 = Directly challenges authority and fundamental team structure",
        ]
    },
}


def load_config(config_path: str = "synthetic_data_config.json") -> Dict:
    """Load configuration."""
    with open(config_path) as f:
        return json.load(f)


# ============================================================================
# TRANSCRIPT LOADING
# ============================================================================

def load_transcript(transcript_path: str) -> Optional[Dict]:
    """Load a single transcript JSON file."""
    try:
        with open(transcript_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load {transcript_path}: {e}")
        return None


def find_all_transcripts(output_dir: str) -> Dict[str, Dict]:
    """Find and load all transcript JSON files."""
    transcripts = {}
    pattern = f"{output_dir}/transcripts/*.json"

    for path in glob.glob(pattern):
        transcript = load_transcript(path)
        if transcript:
            participant_id = transcript["participant_id"]
            transcripts[participant_id] = transcript

    return transcripts


# ============================================================================
# HONESTY CODING
# ============================================================================

def format_transcript_for_coding(transcript: Dict) -> str:
    """Format transcript into readable text for coding."""
    lines = [
        f"PARTICIPANT: {transcript['participant_id']}",
        f"CONDITION: {transcript['condition']}",
        f"MODEL: {transcript['model_name']}",
        "\n=== CONVERSATION ===\n"
    ]

    for turn in transcript.get("transcript", []):
        lines.append(f"QUESTION: {turn['chatbot_prompt']}\n")
        lines.append(f"RESPONSE:\n{turn['participant_response']}\n")
        lines.append(f"ASSISTANT FOLLOW-UP:\n{turn['assistant_followup']}\n")
        lines.append("-" * 60 + "\n")

    return "\n".join(lines)


def code_transcript_honesty(
    transcript: Dict,
    config: Dict,
    coder_id: str = "llm_coder",
    model_id: str = "claude-opus-4-8",
) -> Optional[Dict]:
    """
    Code a transcript for feedback honesty using independent LLM.
    Returns dict with criticality, specificity, riskiness, and composite score.
    """
    participant_id = transcript["participant_id"]
    formatted_transcript = format_transcript_for_coding(transcript)

    # Build rubric text
    rubric_parts = []
    for dim in ["criticality", "specificity", "riskiness"]:
        rubric_parts.append(f"\n{dim.upper()}: {HONESTY_RUBRIC[dim]['definition']}")
        rubric_parts.append("Anchors:")
        rubric_parts.extend(HONESTY_RUBRIC[dim]['anchors'])
    rubric_text = "\n".join(rubric_parts)

    prompt = f"""You are an independent coder evaluating feedback honesty in a workplace feedback scenario.

TRANSCRIPT TO CODE:
{formatted_transcript}

CODING RUBRIC (Appendix G):
{rubric_text}

Your task: Code this participant's feedback on each dimension independently.

Consider:
- CRITICALITY: Does the feedback point out real problems, or just surface observations?
- SPECIFICITY: Does the feedback cite concrete examples with context, or stay abstract?
- RISKINESS: Does the feedback challenge established team practices and authority?

CRITICAL INSTRUCTION: Respond ONLY with valid JSON, nothing else. No markdown, no preamble.
Keep each reasoning field to ONE short sentence (max 15 words) — brevity is required so the JSON is never cut off.

{{"criticality_score": 2, "criticality_reasoning": "brief one-sentence reason", "specificity_score": 3, "specificity_reasoning": "brief one-sentence reason", "riskiness_score": 1, "riskiness_reasoning": "brief one-sentence reason"}}
"""

    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model_id,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        # Handle extended thinking (find TextBlock, skip ThinkingBlock)
        response_text = None
        for block in response.content:
            if hasattr(block, 'text'):
                response_text = block.text
                break

        if not response_text:
            logger.warning(f"  [FAIL] No text block found in coder response for {participant_id}")
            return None

        # Extract JSON from response robustly
        response_text = response_text.strip()

        # Remove markdown code fences
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        # Find JSON object (look for { and })
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            response_text = response_text[json_start:json_end]

        response_text = response_text.strip()

        try:
            coding = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback: salvage scores via regex if response was truncated mid-string
            salvaged = {}
            for key in ["criticality_score", "specificity_score", "riskiness_score"]:
                m = re.search(rf'"{key}"\s*:\s*(\d+(?:\.\d+)?)', response_text)
                if m:
                    salvaged[key] = float(m.group(1))
            if len(salvaged) == 3:
                logger.warning(f"  [WARN] Truncated JSON for {participant_id}, salvaged scores via regex")
                coding = salvaged
            else:
                logger.warning(f"  [FAIL] JSON parse error for {participant_id}: {e}")
                logger.warning(f"    Extracted text: {response_text[:300]}")
                return None

        # Validate and convert scores
        scores = []
        for key in ["criticality_score", "specificity_score", "riskiness_score"]:
            val = coding.get(key)
            if val is None:
                logger.warning(f"  [FAIL] Missing {key} for {participant_id}. Full response: {coding}")
                return None
            try:
                score = int(round(float(val)))
                if not (0 <= score <= 3):
                    logger.warning(f"  [FAIL] Score out of range for {key}: {score}")
                    return None
                scores.append(score)
            except (TypeError, ValueError):
                logger.warning(f"  [FAIL] Invalid score for {key}: {val}")
                return None

        # Compute composite feedback honesty index
        honesty_index = sum(scores) / len(scores)

        return {
            "participant_id": participant_id,
            "condition": transcript["condition"],
            "model_name": transcript["model_name"],
            "coder_id": coder_id,
            "criticality": scores[0],
            "specificity": scores[1],
            "riskiness": scores[2],
            "feedback_honesty_index": round(honesty_index, 2),
            "coding_notes": (
                f"Criticality: {coding.get('criticality_reasoning', '')}; "
                f"Specificity: {coding.get('specificity_reasoning', '')}; "
                f"Riskiness: {coding.get('riskiness_reasoning', '')}"
            ),
            "timestamp_coded": datetime.now(timezone.utc).isoformat(),
        }

    except json.JSONDecodeError as e:
        logger.warning(f"  [FAIL] Failed to parse coder response for {participant_id}: {e}")
        return None
    except Exception as e:
        logger.warning(f"  [FAIL] Coding error for {participant_id}: {type(e).__name__}: {e}")
        return None


# ============================================================================
# OUTPUT
# ============================================================================

def write_honesty_codings_csv(
    codings: Dict[str, Dict],
    output_dir: str,
):
    """Write honesty_codings.csv file."""
    csv_path = f"{output_dir}/synthetic_honesty_codings_4pt_n200.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "participant_id",
            "condition",
            "model_name",
            "coder_id",
            "criticality_score",
            "specificity_score",
            "riskiness_score",
            "feedback_honesty_index",
            "coding_notes",
            "timestamp_coded",
        ])
        writer.writeheader()

        for coding in codings.values():
            writer.writerow({
                "participant_id": coding["participant_id"],
                "condition": coding["condition"],
                "model_name": coding["model_name"],
                "coder_id": coding["coder_id"],
                "criticality_score": coding["criticality"],
                "specificity_score": coding["specificity"],
                "riskiness_score": coding["riskiness"],
                "feedback_honesty_index": coding["feedback_honesty_index"],
                "coding_notes": coding["coding_notes"],
                "timestamp_coded": coding["timestamp_coded"],
            })

    print(f"[OK] Wrote {csv_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    # Setup Windows console Unicode
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    config = load_config()
    output_dir = config["output"]["directory"]
    logger = setup_logging(output_dir)

    logger.info("=" * 70)
    logger.info("Honesty Coding Agent (Appendix G Rubric)")
    logger.info("=" * 70)
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Log file: {output_dir}/honesty_coding.log")

    # Load transcripts
    try:
        logger.info(f"\n[*] Loading transcripts from {output_dir}/transcripts/...")
        transcripts = find_all_transcripts(output_dir)
        logger.info(f"[OK] Loaded {len(transcripts)} transcripts")

        if len(transcripts) == 0:
            logger.error("[FAIL] No transcripts found. Did you run generate_synthetic_data.py first?")
            return

        # Group by condition
        warm_count = sum(1 for t in transcripts.values() if t['condition'] == 'warm')
        competent_count = sum(1 for t in transcripts.values() if t['condition'] == 'competent')
        logger.debug(f"  - Warm condition: {warm_count}")
        logger.debug(f"  - Competent condition: {competent_count}")

    except Exception as e:
        logger.error(f"Failed to load transcripts: {e}")
        return

    # Code each transcript
    logger.info(f"\n[*] Coding feedback honesty (this takes 15-20 minutes)...\n")
    codings = {}
    failed_codings = []

    for idx, (participant_id, transcript) in enumerate(transcripts.items(), 1):
        model_name = transcript.get('model_name', 'Unknown')
        condition = transcript.get('condition', '?')

        logger.info(f"[{idx:3d}/{len(transcripts)}] {model_name:15s} ({condition:10s}) | {participant_id[:12]}...")

        coding = code_transcript_honesty(transcript, config)

        if coding:
            codings[participant_id] = coding
            logger.info(f"  [OK] C={coding['criticality']} S={coding['specificity']} "
                       f"R={coding['riskiness']} H={coding['feedback_honesty_index']}")
        else:
            logger.warning(f"  [FAIL] Coding failed")
            failed_codings.append(participant_id)

    # Write output
    logger.info(f"\n[*] Writing outputs...")
    try:
        write_honesty_codings_csv(codings, output_dir)
        logger.info(f"[OK] Outputs written successfully")
    except Exception as e:
        logger.error(f"Failed to write outputs: {e}")
        return

    # Summary statistics
    if codings:
        honesty_scores = [c["feedback_honesty_index"] for c in codings.values()]
        criticality_scores = [c["criticality"] for c in codings.values()]
        specificity_scores = [c["specificity"] for c in codings.values()]
        riskiness_scores = [c["riskiness"] for c in codings.values()]

        warm_codings = [c for c in codings.values() if c['condition'] == 'warm']
        competent_codings = [c for c in codings.values() if c['condition'] == 'competent']

        logger.info(f"\n" + "=" * 70)
        logger.info(f"[OK] CODING COMPLETE")
        logger.info(f"=" * 70)
        logger.info(f"Total coded: {len(codings)}/{len(transcripts)}")
        if failed_codings:
            logger.warning(f"Failed: {len(failed_codings)}")

        logger.info(f"\nFeedback Honesty Index (composite, 0-3 scale):")
        logger.info(f"  - Overall mean: {sum(honesty_scores)/len(honesty_scores):.2f}")
        logger.info(f"  - Range: {min(honesty_scores):.2f} - {max(honesty_scores):.2f}")

        if warm_codings:
            warm_mean = sum(c['feedback_honesty_index'] for c in warm_codings) / len(warm_codings)
            logger.info(f"  - Warm condition mean: {warm_mean:.2f}")
        if competent_codings:
            comp_mean = sum(c['feedback_honesty_index'] for c in competent_codings) / len(competent_codings)
            logger.info(f"  - Competent condition mean: {comp_mean:.2f}")

        logger.info(f"\nDimension means:")
        logger.info(f"  - Criticality:  {sum(criticality_scores)/len(criticality_scores):.2f}")
        logger.info(f"  - Specificity:  {sum(specificity_scores)/len(specificity_scores):.2f}")
        logger.info(f"  - Riskiness:    {sum(riskiness_scores)/len(riskiness_scores):.2f}")

        logger.info(f"\nOutput files in {output_dir}:")
        logger.info(f"  [OK] synthetic_honesty_codings.csv ({len(codings)} rows)")
        logger.info(f"  [OK] honesty_coding.log (this log)")

        logger.info(f"\nAll synthetic data ready for analysis!")
        logger.info("=" * 70)


if __name__ == "__main__":
    main()
