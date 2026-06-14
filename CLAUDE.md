# Persona-Employee-Feedback-Chatbot Context

## Project Overview
Research study evaluating how AI chatbot personas (warm vs. competent) affect psychological safety, feedback quality, and engagement in workplace feedback scenarios. This is a thesis/research project.

### Key Variables
- **Independent Variable**: Persona condition (warm vs. competent)
- **Dependent Variables**: 
  - Engagement indicators (word count, number of turns)
  - Feedback honesty scores
  - Psychological safety (measured via 5-item scale)
  - Task completion (binary)
  - Manipulation checks (perceived warmth, competence)

## System Architecture

### Tech Stack
- **Backend**: FastAPI (Python), PostgreSQL
- **Frontend**: Streamlit
- **Deployment**: Docker + Docker Compose
- **External**: OpenAI API (embeddings + chat completions)

### Services
1. **PostgreSQL** (port 5432): Database for sessions, responses, questionnaire data
2. **FastAPI Backend** (port 8000): Chat API, session management, data export
3. **Streamlit Frontend** (port 8501): Study interface

## Study Flow

1. **Consent Screen**: Participant agrees to study
2. **Condition Assignment**: Random assignment to warm OR competent persona
3. **Vignette Display**: Read workplace scenario about workload/coordination issues
4. **Chat Phase**: 3-5 turn conversation with AI assistant
   - Assistant follows structured prompts: issue detail → impact → causes → improvement
   - Persona style (warm vs competent) differs in tone only
5. **Questionnaire**: Perception scales + demographics
6. **Completion**: Thank you page with psychological safety score

## Vignette Details
**Scenario**: Working student/intern in team with unclear task assignments, changing priorities, inconsistent communication, unclear responsibilities.

**Structured Follow-ups** (must maintain order):
1. "What exactly is happening? Describe the main issue concretely."
2. "How does this affect your work, motivation, or team functioning?"
3. "What causes or factors contribute to this problem?"
4. "What changes would most improve this situation?"

## Persona Instructions

### Warm Persona
- Tone: Friendly, understanding, supportive
- Approach: Acknowledge feelings, use inclusive "we"/"let's", provide socio-emotional support

### Competent Persona
- Tone: Precise, analytical, professional
- Approach: Clarify facts, emphasize improvement, focus on diagnosis

**Critical**: Both personas must follow same follow-up sequence and factual focus. Only tone differs.

## Data Collection & Analysis

**Stage 1**: Descriptive statistics by condition (engagement, honesty, psychological safety)

**Stage 2**: Regression models predicting outcomes from persona condition, controlling for:
- Prior conversational AI experience
- Organizational tenure
- Demographics (age, gender, industry, role)

**Stage 3**: Mediation analysis - test if psychological safety mediates persona effect on feedback quality (bootstrap with 5,000 resamples)

## Retrieval Logging & Metadata

**Retrieval metadata is logged for auditability and reproducibility. It is not used as a primary outcome variable unless explicitly analysed.**

### Privacy-Conscious Logging
- User messages are stored in the `messages` table and linked via `message_id`, not duplicated in retrieval logs
- Retrieval logs contain only aggregate metadata needed for auditability:
  - `participant_id`, `condition`, `turn_index`, `message_id`
  - Retrieved card IDs and constructs (not full document text)
  - Retrieval scores and method (embedding or fallback)
  - Corpus version for reproducibility

### Exported Fields (CSV)
- participant_id
- condition
- turn_index
- message_id
- retrieved_card_ids
- retrieved_card_constructs
- retrieval_scores
- retrieval_method
- retrieval_enabled
- retrieval_top_k
- corpus_version
- timestamp_created

## Docker Setup (Resolved)
- Postgres added to `chatbot_network`
- OPENAI_API_KEY loaded from `backend/.env` only (not from shell)
- DATABASE_URL points to postgres service in Docker (not localhost)

## Current Implementation Status
- ✅ Backend API (FastAPI) with session/chat/questionnaire endpoints
- ✅ Frontend (Streamlit) with full study flow
- ✅ PostgreSQL database
- ✅ Docker setup working
- ⏳ Persona validation & testing
- ⏳ Data export/analysis pipeline
