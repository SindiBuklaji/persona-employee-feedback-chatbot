# Quick Start: Generate Synthetic Data

## Prerequisites

```bash
# Set your API keys (do this FIRST)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Or on Windows PowerShell:
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:OPENAI_API_KEY = "sk-..."

# Verify they're set
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

---

## Command 1: Generate Synthetic Sessions (45 min)

```bash
python generate_synthetic_data.py
```

**What it does:**
- Runs 100 participants through full chatbot flow (4 turns each)
- Uses 4 LLM models (Claude Haiku/Sonnet, GPT-4o-mini/4o)
- Balanced: 50 warm / 50 competent
- **Fills questionnaire automatically** (Likert scales 1-7)
- Saves full transcripts for later coding

**Real-time output you'll see:**

```
======================================================================
Synthetic Participant Data Generation Pipeline
Thesis Methodology: Sections 3.7 and 5.6
======================================================================
Output directory: ./synthetic_data
Log file: ./synthetic_data/generation.log

✓ Config loaded
✓ Target: 100 participants (50 per condition)
✓ Models: Claude Haiku, Claude Sonnet, GPT-4o-mini, GPT-4o

📋 Creating participant allocation...
✓ Created 100 balanced allocations
  Warm: 50
  Competent: 50

📊 Running 100 synthetic sessions...
(This will take 30-45 minutes. Progress logged below.)

[  1/100] Claude Haiku   (warm      ) | a1b2c3d4-... ✓ (H=6, PS=5.3)
[  2/100] Claude Sonnet  (competent ) | b2c3d4e5-... ✓ (H=5, PS=4.7)
[  3/100] GPT-4o-mini    (warm      ) | c3d4e5f6-... ✓ (H=7, PS=6.1)
[  4/100] GPT-4o         (competent ) | d4e5f6g7-... ✓ (H=4, PS=3.8)
...
[ 98/100] Claude Haiku   (warm      ) | wx8yz9ab-... ✓ (H=5, PS=5.0)
[ 99/100] Claude Sonnet  (competent ) | xy9za0bc-... ⚠ Session OK, questionnaire failed
[100/100] GPT-4o-mini    (warm      ) | yz0ab1cd-... ✓ (H=6, PS=5.5)

💾 Writing outputs...
✓ All outputs written successfully

======================================================================
✓ GENERATION COMPLETE
======================================================================
Sessions completed: 98/100 (98%)
  - Warm condition: 49/50
  - Competent condition: 49/50
  - Balance: 49W / 49C

Questionnaires:
  - Completed: 97
  - Failed: 1

📁 Output files in ./synthetic_data:
  ✓ synthetic_participants.csv (98 rows)
  ✓ synthetic_questionnaires.csv (97 rows)
  ✓ transcripts/ (98 JSON files)
  ✓ generation.log (this log)
  ✓ generation_procedure.json (reproducibility)

🔜 Next step: python code_transcript_honesty.py
======================================================================
```

**What it created:**
- `synthetic_data/synthetic_participants.csv` — engagement metrics
- `synthetic_data/synthetic_questionnaires.csv` — **questionnaire answers** (all 8 Likert scales filled)
- `synthetic_data/transcripts/` — raw conversation JSONs
- `synthetic_data/generation.log` — detailed execution log
- `synthetic_data/generation_procedure.json` — reproducibility document

---

## Command 2: Code Transcripts for Honesty (20 min)

```bash
python code_transcript_honesty.py
```

**What it does:**
- Reads all transcripts from `synthetic_data/transcripts/`
- **Independent LLM** codes each on Appendix G rubric:
  - **Criticality** (1-5): How intense is the critique?
  - **Specificity** (1-5): How concrete vs. vague?
  - **Riskiness** (1-5): Does it challenge status quo?
- Computes composite **Feedback Honesty Index** (mean of 3)

**Real-time output you'll see:**

```
======================================================================
Honesty Coding Agent (Appendix G Rubric)
======================================================================
Output directory: ./synthetic_data
Log file: ./synthetic_data/honesty_coding.log

📂 Loading transcripts from ./synthetic_data/transcripts/...
✓ Loaded 98 transcripts
  - Warm condition: 49
  - Competent condition: 49

🔍 Coding feedback honesty (this takes 15-20 minutes)...

[  1/98] Claude Haiku   (warm      ) | a1b2c3d4-... ✓ C=4 S=4 R=3 H=3.67
[  2/98] Claude Sonnet  (competent ) | b2c3d4e5-... ✓ C=3 S=3 R=2 H=2.67
[  3/98] GPT-4o-mini    (warm      ) | c3d4e5f6-... ✓ C=5 S=5 R=4 H=4.67
[  4/98] GPT-4o         (competent ) | d4e5f6g7-... ✓ C=2 S=2 R=1 H=1.67
...
[ 96/98] Claude Sonnet  (warm      ) | uv6wx7xy-... ✓ C=4 S=4 R=3 H=3.67
[ 97/98] GPT-4o-mini    (competent ) | vw7xy8yz-... ✓ C=3 S=3 R=2 H=2.67
[ 98/98] GPT-4o         (warm      ) | wx8yz9ab-... ✓ C=5 S=4 R=3 H=4.00

💾 Writing outputs...
✓ Outputs written successfully

======================================================================
✓ CODING COMPLETE
======================================================================
Total coded: 98/98

📊 Feedback Honesty Index (composite, 1-5 scale):
  - Overall mean: 3.24
  - Range: 1.67 - 4.67
  - Warm condition mean: 3.42
  - Competent condition mean: 3.06

📈 Dimension means:
  - Criticality:  3.31
  - Specificity:  3.28
  - Riskiness:    3.12

📁 Output files in ./synthetic_data:
  ✓ synthetic_honesty_codings.csv (98 rows)
  ✓ honesty_coding.log (this log)

✓ All synthetic data ready for analysis!
======================================================================
```

**What it created:**
- `synthetic_data/synthetic_honesty_codings.csv` — **coded honesty scores**
- `synthetic_data/honesty_coding.log` — detailed execution log

---

## What Gets Filled (Questionnaire)

The LLM automatically fills out the same questionnaire as human participants:

```
Manipulation Checks (1-7 Likert):
  - perc_warmth_bipolar: "How warm was the assistant?" (1=warm, 7=formal)
  - perc_task_focus_bipolar: "How task-focused?" (1=comforting, 7=analytical)

Psychological Safety (1-7 Likert):
  - psych_safe_1: "I felt safe to express concerns"
  - psych_safe_2: "I could be honest without fear"
  - psych_safe_3: "I felt comfortable sharing critical feedback"

Honesty/Openness (1-7 Likert):
  - openness_1: "I answered honestly"
  - openness_2_raw: "I held back my true thoughts" (raw; reverse-coded in analysis)

Engagement (1-7 Likert):
  - engagement_self_report: "I felt engaged"

(Plus random demographics: age, gender, industry, job role, experience)
```

All filled in automatically as JSON during generation.

---

## Files You'll Have After Both Commands

```
synthetic_data/
├── synthetic_participants.csv         ← Engagement metrics (98 rows)
├── synthetic_questionnaires.csv       ← Questionnaire responses (98 rows, all 8 Likert scales filled)
├── synthetic_honesty_codings.csv      ← Coded honesty scores (98 rows, Appendix G rubric)
├── generation.log                     ← Generation execution log
├── honesty_coding.log                 ← Honesty coding execution log
├── generation_procedure.json          ← Reproducibility document
└── transcripts/
    ├── a1b2c3d4-....json            ← Raw conversation 1
    ├── b2c3d4e5-....json            ← Raw conversation 2
    └── ... (98 total)
```

---

## Next: Merge with Human Data (Optional)

After both commands complete, you can merge with human data:

```python
import pandas as pd

# Load human data (from export endpoints)
human_q = pd.read_csv("questionnaires.csv")
human_q["data_source"] = "human"

# Load synthetic data
synthetic_q = pd.read_csv("synthetic_data/synthetic_questionnaires.csv")
synthetic_q["data_source"] = "synthetic"

# Combine
all_questionnaires = pd.concat([human_q, synthetic_q], ignore_index=True)
all_questionnaires.to_csv("questionnaires_combined.csv", index=False)

# You now have N=120+ with balanced conditions for analysis
```

---

## Costs & Timeline

| Step | Duration | Cost |
|------|----------|------|
| Command 1: Generation | 30-45 min | $35-55 USD |
| Command 2: Honesty coding | 15-20 min | $10-15 USD |
| **Total** | **45-65 min** | **$45-70 USD** |

---

## Troubleshooting

**"Missing API key env var"**
```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

**"Failed to call backend"**
Ensure Railway app is running:
```bash
curl -H "Authorization: Bearer test-token" \
  https://persona-employee-feedback-chatbot-production.up.railway.app/chat
```

**"No transcripts found"**
Run Command 1 first. Check that `synthetic_data/transcripts/` has `.json` files.

**Partial failures**
Both scripts are resilient. Some questionnaires or codings may fail (logged). Rerun to retry or accept ~95% completion as normal.

---

## Summary

✅ **Two commands, ~1 hour total**
✅ **Yes, questionnaires are auto-filled**
✅ **Real-time progress logging**
✅ **Ready for thesis analysis after both complete**

Ready to run? Go ahead with:
```bash
python generate_synthetic_data.py
```
