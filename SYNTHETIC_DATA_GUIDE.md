# Synthetic Data Generation Pipeline

## Overview

This pipeline generates 100 synthetic participant conversations via multiple LLMs (Claude Haiku, Claude Sonnet, GPT-4o-mini, GPT-4o) to supplement your human sample for balanced, adequately-powered statistical analysis.

**Thesis reference**: Sections 3.7 and 5.6 (Synthetic Sample Methodology)  
**Supervisor approval**: Methodologically approved supplement to human data

---

## Before You Start

### 1. Environment Variables

Set up API keys in your shell or `.env` file:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

**Where to get them:**
- **Anthropic API Key**: https://console.anthropic.com/account/keys
- **OpenAI API Key**: https://platform.openai.com/account/api-keys

### 2. Ensure Backend is Running

The generation script calls your FastAPI backend to get chatbot responses. Verify it's accessible:

```bash
curl -H "Authorization: Bearer test-token" \
  https://persona-employee-feedback-chatbot-production.up.railway.app/chat
```

Or if running locally:
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Install Dependencies (if not already installed)

```bash
pip install anthropic openai requests
```

---

## Step 1: Generate Synthetic Sessions

This runs all 100 participants through the full chatbot flow, collecting transcripts and metrics.

```bash
python generate_synthetic_data.py
```

**What it does:**
- Creates 100 balanced participants (50 warm / 50 competent)
- Distributes evenly across 4 models (25 per model)
- For each participant:
  - Loads vignette
  - Runs 4-turn conversation with your chatbot
  - Collects full transcript
  - Generates questionnaire response
- Outputs CSV files and transcript JSONs for coding

**Expected output:**
- `synthetic_data/synthetic_participants.csv` — Engagement metrics by participant
- `synthetic_data/synthetic_questionnaires.csv` — Questionnaire responses
- `synthetic_data/transcripts/` — Individual transcript JSONs
- `synthetic_data/generation_procedure.json` — Reproducibility log

**Runtime:** ~30-45 minutes depending on API latency. Both Anthropic and OpenAI APIs will have parallel calls.

---

## Step 2: Code Transcripts for Honesty (Appendix G Rubric)

After generation completes, independently code all transcripts using the feedback honesty rubric.

```bash
python code_transcript_honesty.py
```

**What it does:**
- Loads all transcripts from `synthetic_data/transcripts/`
- For each transcript, uses an independent LLM to code:
  - **Criticality** (1-5): Intensity of problem evaluation
  - **Specificity** (1-5): Concrete examples vs. vague statements
  - **Riskiness** (1-5): Challenges to established practices
- Computes composite **Feedback Honesty Index** (mean of the three)
- Outputs honesty_codings.csv

**Expected output:**
- `synthetic_data/synthetic_honesty_codings.csv` — Coded honesty scores

**Runtime:** ~15-20 minutes

---

## Step 3: Merge with Human Data (Optional)

Once you have both human and synthetic CSVs, you can combine them for analysis:

```bash
# Add a source_type column to identify human vs. synthetic
# Append synthetic CSVs to human CSVs
# Keep them separate in analysis with source_type as a control variable
```

Example in pandas:

```python
import pandas as pd

# Load human data (from export endpoints)
human_participants = pd.read_csv("participants.csv")
human_questionnaires = pd.read_csv("questionnaires.csv")
human_honesty = pd.read_csv("honesty_codings.csv")

# Load synthetic data
synthetic_participants = pd.read_csv("synthetic_data/synthetic_participants.csv")
synthetic_questionnaires = pd.read_csv("synthetic_data/synthetic_questionnaires.csv")
synthetic_honesty = pd.read_csv("synthetic_data/synthetic_honesty_codings.csv")

# Add source column
human_participants["data_source"] = "human"
synthetic_participants["data_source"] = "synthetic"

human_questionnaires["data_source"] = "human"
synthetic_questionnaires["data_source"] = "synthetic"

human_honesty["data_source"] = "human"
synthetic_honesty["data_source"] = "synthetic"

# Combine
all_participants = pd.concat([human_participants, synthetic_participants], ignore_index=True)
all_questionnaires = pd.concat([human_questionnaires, synthetic_questionnaires], ignore_index=True)
all_honesty = pd.concat([human_honesty, synthetic_honesty], ignore_index=True)

# Save combined datasets
all_participants.to_csv("participants_combined.csv", index=False)
all_questionnaires.to_csv("questionnaires_combined.csv", index=False)
all_honesty.to_csv("honesty_codings_combined.csv", index=False)
```

---

## Output Files Reference

### `synthetic_participants.csv`
Engagement metrics and completion status.

| Column | Type | Notes |
|--------|------|-------|
| participant_id | str | UUID |
| condition | str | warm or competent |
| model_name | str | e.g., "Claude Haiku" |
| model_id | str | e.g., "claude-haiku-4-5-20251001" |
| completed_task | int | 0 or 1 |
| number_user_turns | int | Total conversational turns |
| total_user_word_count | int | All user message words |
| average_user_message_length | float | Words per message |
| started_at | str | ISO timestamp |
| completed_at | str | ISO timestamp |
| dropout_stage | str | null if completed; error reason if not |

### `synthetic_questionnaires.csv`
Questionnaire responses (psychological safety, honesty, engagement, manipulation checks, demographics).

| Column | Type | Notes |
|--------|------|-------|
| participant_id | str | UUID |
| condition | str | warm or competent |
| model_name | str | e.g., "Claude Haiku" |
| model_id | str | LLM used |
| perc_warmth_bipolar | int | 1-7 (1=warm, 7=formal) |
| perc_task_focus_bipolar | int | 1-7 (1=comforting, 7=analytical) |
| psych_safe_1/2/3 | int | 1-7 psychological safety items |
| psychological_safety_mean | float | Mean of above three |
| openness_1 | int | 1-7 (answered honestly) |
| openness_2_raw | int | 1-7 (held back; will be reverse-coded) |
| self_reported_honesty_mean | float | Mean of openness items (reverse-coded) |
| engagement_self_report | int | 1-7 (felt engaged) |
| ai_experience | int | 1-7 scale |
| years_work_experience | float | 0.5-5.0 |
| age | int | 19-35 |
| gender | str | Male, Female, Non-binary, Prefer not to say |
| industry | str | Various |
| job_role | str | Student, Intern, etc. |
| timestamp_submit | str | ISO timestamp |

### `synthetic_honesty_codings.csv`
Coded feedback honesty on Appendix G rubric.

| Column | Type | Notes |
|--------|------|-------|
| participant_id | str | UUID |
| condition | str | warm or competent |
| model_name | str | e.g., "Claude Haiku" |
| coder_id | str | "llm_coder" (independent LLM) |
| criticality_score | int | 1-5 (intensity of critique) |
| specificity_score | int | 1-5 (concrete vs. vague) |
| riskiness_score | int | 1-5 (challenges status quo) |
| feedback_honesty_index | float | Mean of above three |
| coding_notes | str | Reasoning for each dimension |
| timestamp_coded | str | ISO timestamp |

### `transcripts/`
Individual JSON files per participant containing full raw transcript. Used for independent coding; can be archived or deleted after honesty coding completes.

```json
{
  "participant_id": "uuid",
  "condition": "warm",
  "model_name": "Claude Haiku",
  "transcript": [
    {
      "turn_index": 0,
      "chatbot_prompt": "What exactly is happening...",
      "participant_response": "...",
      "assistant_followup": "..."
    }
  ]
}
```

### `generation_procedure.json`
Reproducibility log documenting exact config, models used, balance checks, etc. Include this in your thesis methodology appendix.

---

## Thesis Integration

### Methodology Section (Sections 3.7 / 5.6)

Template language:

> **Synthetic Sample Generation**
>
> To supplement the human sample (N = 20, imbalanced across conditions), we generated synthetic participant data using a multi-LLM protocol. Four distinct LLMs were deployed: Claude Haiku, Claude Sonnet (Anthropic), GPT-4o-mini, and GPT-4o (OpenAI). Each LLM played the role of a synthetic participant responding to the same vignette, follow-up prompts, and post-chat questionnaire used with human participants (N = 100 synthetic; 50 per condition, balanced within LLM provider).
>
> Each synthetic session consisted of: (1) presentation of the workplace scenario vignette, (2) four-turn conversation with the chatbot (warm or competent condition), (3) participant LLM generating naturalistic responses, (4) completion of the structured post-chat questionnaire as JSON output. Full raw transcripts were saved and independently coded using the feedback honesty rubric (Appendix G) by a separate LLM-based coder to prevent response bias.
>
> [Reference the generation_procedure.json for model allocation, completion rates, and balance confirmation]

### Results Section

Report human and synthetic results separately, then together:

```
Human sample: N = 20 (10 warm, 3 competent)*
Synthetic sample: N = 100 (50 warm, 50 competent)
Combined: N = 120 for main hypothesis tests; human-only models for robustness checks

*Imbalance in human warm/competent due to condition assignment bias;
synthetic sample balances this for adequately powered statistical tests.
```

Include a table showing model distribution across conditions in the appendix (from `generation_procedure.json`).

---

## Troubleshooting

### "Missing API key env var"
Ensure `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are set:
```bash
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

### "Failed to call backend"
Check that the Railway app is running and accessible. Verify the URL in `synthetic_data_config.json`:
```bash
curl -H "Authorization: Bearer test-token" \
  https://persona-employee-feedback-chatbot-production.up.railway.app/chat -d '{}' -H "Content-Type: application/json"
```

### "Questionnaire JSON parse failed"
The participant LLM sometimes returns malformed JSON. This is expected occasionally; the pipeline logs these as questionnaire failures but doesn't crash. Rerun `generate_synthetic_data.py` to retry or lower the max_tokens in the questionnaire prompt.

### "No transcripts found" during honesty coding
Ensure `generate_synthetic_data.py` completed successfully and `synthetic_data/transcripts/` contains `.json` files.

---

## Best Practices

1. **Run generation when APIs are stable** — both Anthropic and OpenAI may have rate limits. Monitor progress and rerun failed participants if needed.

2. **Keep transcripts** — Save the raw transcripts/ directory for reproducibility and potential post-hoc analysis. Include a note in your thesis appendix that transcripts are available upon request.

3. **Separate by source in analysis** — Always control for `data_source` (human vs. synthetic) in statistical models. Report both within-source and combined results.

4. **Document everything** — The `generation_procedure.json` is your reproducibility anchor. Cite it in your methodology.

5. **Validate condition balance** — Check `generation_procedure.json` to confirm warm/competent balance across models before analysis.

---

## Questions?

If a generation run fails partway through, the logs will indicate where. You can manually resume or restart. The pipeline is idempotent — rerunning on the same config will regenerate all participants (overwriting prior outputs).

For thesis questions, cite this guide and the methodology sections above.
