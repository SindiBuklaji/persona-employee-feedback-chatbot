# Prompt for Writing Agent: Update Thesis Appendices to Match Code Implementation

## Task
Rewrite Appendices E, F, and G (Post-chat questionnaire, Operationalization of dependent variables, and Coding manual for feedback honesty) to accurately reflect the **current implementation** in the codebase, not the previously planned design.

---

## Current Implementation Details (From Code)

### Appendix E: Post-Chat Questionnaire Items, Scales, and Coding

The post-chat questionnaire contains the following sections and items:

#### Section 1: Manipulation Checks (Bipolar Slider Format)
- **2 bipolar slider items** (not 8 separate items as in original appendix)
- Scale: 1-7
- Items:
  1. **Assistant's interpersonal approach** (perc_warmth_bipolar): 1 = Warm and supportive → 7 = Direct and formal
  2. **Assistant's focus** (perc_task_focus_bipolar): 1 = Comforting and empathetic → 7 = Task-focused and efficient
- Notes: These are diagnostic checks, not dependent variables. Assessed with bipolar sliders to evaluate perception of warmth vs. directness and empathy vs. task-focus.

#### Section 2: Psychological Safety (Likert Scale)
- **3 items** (NOT 5 as in original appendix)
- Scale: 1-7 (1 = strongly disagree to 7 = strongly agree)
- Items:
  1. **psych_safe_1**: "I felt safe to express concerns during the conversation."
  2. **psych_safe_2**: "I could be honest without worrying about being judged."
  3. **psych_safe_3**: "I felt comfortable sharing critical feedback."
- Scoring: Mean of psych_safe_1, psych_safe_2, psych_safe_3

#### Section 3: Openness/Honesty (Likert Scale)
- **2 items** (NOT in original appendix design)
- Scale: 1-7 (1 = strongly disagree to 7 = strongly agree)
- Items:
  1. **openness_1**: "I answered the assistant honestly."
  2. **openness_2**: "I held back some things I was thinking." (REVERSE CODED: 8 - response value)
- Note: openness_2 is reverse-coded because high agreement indicates low honesty
- Scoring: Mean of openness_1 and (8 - openness_2), rounded to 4 decimals

#### Section 4: Engagement Self-Report
- **1 item**
- Scale: 1-7
- Item: **engagement_self_report**: "I felt engaged during the conversation."

#### Section 5: Control Variables
- **6 items** (not 8 as in original appendix)
- Items:
  1. **ai_experience**: Prior conversational AI experience (1-7 scale)
  2. **years_work_experience**: Total years of work experience (numeric, continuous)
  3. **age**: Age in years (18-100 range)
  4. **gender**: Gender (categorical: Female, Male, Non-binary, Prefer to self-describe, Prefer not to say)
  5. **industry**: Industry (open text field)
  6. **job_role**: Current or most recent job role (open text field)

**Note on changes from original design:**
- Manipulation checks simplified from 8 separate items to 2 bipolar sliders
- Psychological safety reduced from 5 to 3 items
- Openness/honesty items added (not in original design)
- Prior AI experience collapsed to single 1-7 item (was 2 items in original)
- Career stage (C4) removed
- Organizational tenure now collected as continuous years_work_experience

---

### Appendix F: Operationalization of Dependent Variables

**Three main dependent variables:**

| DV | Source | Operationalization | Level of Measurement | Calculation |
|---|---|---|---|---|
| **Engagement** | System log | (1) Task completion (yes/no), (2) Total word count of participant messages, (3) Number of conversational turns | Behavioral: binary + continuous | Task completion = binary; word count and turns = continuous variables analyzed separately |
| **Feedback honesty** | Chat transcript (coder-rated) | Three dimensions: criticality, specificity, riskiness | Ordinal coder ratings aggregated to continuous index | Mean of criticality, specificity, and riskiness scores; higher values = more candid, specific, risk-taking feedback |
| **Psychological safety** | Post-chat questionnaire | Three items referring to safety during interaction with AI assistant (psych_safe_1–psych_safe_3) | Self-report Likert scale (1-7) | Mean of psych_safe_1, psych_safe_2, psych_safe_3 |

**Additional measured construct (not primary DV):**
- **Self-reported honesty**: Mean of openness_1 and reverse-coded openness_2

---

### Appendix G: Coding Manual for Feedback Honesty

Feedback honesty was operationalized via qualitative content analysis of each participant's chat transcript. Responses were coded along three dimensions: **criticality, specificity, and riskiness**. Each dimension was rated on a **5-point ordinal scale (1–5)**.

#### Scoring Framework

**Dimension 1: Criticality (FH1)**

| Score | Label | Operational Definition | Typical Indicators |
|---|---|---|---|
| 1 | No criticism | No clear criticism or problem identification; response is descriptive, neutral, or purely positive. | No explicit issues, no negative evaluation |
| 2 | Mild criticism | A problem is hinted at but framed vaguely. | Softened negative wording, vague concern |
| 3 | Clear criticism | A concrete problem is identified and evaluated negatively. | Direct problem statement, stated negative consequences |
| 4 | Strong criticism | Feedback emphasizes serious dysfunction or repeated failure. | Strong negative tone, systemic or recurrent issues |
| 5 | [Severe/Most critical] | [Clarify if needed or leave 1-4 scale] | [Define if using 5-point] |

**Dimension 2: Specificity (FH2)**

| Score | Label | Operational Definition | Typical Indicators |
|---|---|---|---|
| 1 | Highly vague | No concrete detail provided. | General statements only, no example |
| 2 | Limited detail | Issue mentioned but remains general. | Broad description, little elaboration |
| 3 | Moderately specific | Includes at least one concrete example or situation. | One example, clear reference to who/what/when |
| 4 | Highly specific | Provides multiple or richly detailed examples. | Several concrete events, explicit mechanisms |
| 5 | [Exhaustively detailed] | [If using 5-point, define this level] | [Define if applicable] |

**Dimension 3: Riskiness (FH3)**

| Score | Label | Operational Definition | Typical Indicators |
|---|---|---|---|
| 1 | No risk | No interpersonal or organizational risk; feedback remains harmless or generic. | No challenge to actors, rules, or practices |
| 2 | Low risk | Process concerns without clearly challenging people or established practices. | Mildly critical of "processes" in general |
| 3 | Moderate risk | Implies failures by decision makers, managers, or formal procedures. | References to management expectations, unclear leadership |
| 4 | High risk | Directly challenges powerful actors, entrenched norms, or systemic behaviors. | Explicit criticism of managers or central policies |
| 5 | [Extremely high risk] | [If using 5-point, define escalation] | [Define if applicable] |

#### Feedback Honesty Index
- **Calculation**: Mean of criticality, specificity, and riskiness scores (FH1, FH2, FH3)
- **Range**: 1–5 (higher scores indicate more honest, specific, and risk-taking feedback)
- **Rounding**: Rounded to appropriate precision (match implementation precision)

#### Coding Procedure
- Human-sample transcripts: Coded by thesis author as single rater
- Synthetic-sample transcripts: Coded by LLM coder
- Inter-rater reliability: Not formally established; see limitations discussion

---

## Instructions for Writing Agent

1. **Rewrite Table E1** to reflect 2 manipulation check items (bipolar sliders), 3 psychological safety items, 2 openness/honesty items, 1 engagement item, and 6 control variables

2. **Rewrite Table F1** to show the correct operationalization of engagement, feedback honesty, and psychological safety

3. **Rewrite Table G1** to show 5-point ordinal scale (not 0-3) for criticality, specificity, and riskiness with updated definitions

4. **Update all accompanying text** to:
   - Explain why manipulation checks use bipolar sliders instead of separate items
   - Explain the reduction from 5 to 3 psychological safety items
   - Explain the addition of openness/honesty items
   - Note the change from 0-3 to 1-5 coding scale for feedback honesty
   - Maintain academic tone and thesis-appropriate language

5. **Ensure consistency** across all three appendices regarding:
   - Scale ranges
   - Item labels and abbreviations
   - Scoring procedures
   - Calculation methods

6. **Keep the structure** of the original appendices but update all values and descriptions to match current implementation

---

## Key Changes to Highlight

- Manipulation checks: 8 items → 2 bipolar sliders
- Psychological safety items: 5 → 3
- Feedback honesty coding scale: 0-3 → 1-5
- Control variables: 8 → 6
- Addition of openness/honesty items not in original design

