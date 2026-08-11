# Persona-Employee-Feedback-Chatbot

A master's thesis research study investigating how AI chatbot personas (warm vs. competent) affect psychological safety, feedback honesty, and engagement in workplace feedback scenarios.

## Project Overview

### Research Design
- **Sample**: 
  - Human participants: N=89 (46 warm, 43 competent)
  - Synthetic participants: N=200 (100 warm, 100 competent; 50 per model across Claude Haiku/Sonnet, GPT-4o Mini/4o)

### Study Flow
1. Participant provides consent
2. Random condition assignment (warm or competent persona)
3. Read workplace vignette (task assignment clarity, coordination issues)
4. Structured chat conversation with AI assistant:
   - Issue detail → Impact → Causes → Improvement
5. Post-chat questionnaire (manipulation checks, psychological safety, demographics)

## Codebase Structure

### Backend (`backend/`)
- **Framework**: FastAPI + SQLAlchemy + PostgreSQL
- **Key Files**:
  - `app/routers/session.py` — session management
  - `app/routers/chat.py` — chat endpoint
  - `app/routers/questionnaire.py` — questionnaire submission & manipulation check calculations
  - `app/services/personas.py` — warm vs. competent system prompts
  - `app/models.py` — database schema

### Frontend (`frontend/`)
- **Framework**: Streamlit
- **File**: `streamlit_app.py` — participant-facing study interface

## Reproduction & Analysis

### Reproduce Synthetic Data
```bash
# Ensure API keys are set
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key

# Generate N=200 synthetic participants
cd backend
source .venv/Scripts/activate
python ../synthetic_data/generate_synthetic_data.py

# Code transcripts for feedback honesty
python ../synthetic_data/code_transcript_honesty.py
```

**Note**: Config and scripts are designed to reproduce the v2 design (N=200, 4 models × 50). Individual LLM outputs are non-deterministic; transcripts will differ from the original v2 run.

## Important Notes

### Live Infrastructure (Decommissioned)
- The live Streamlit frontend and FastAPI backend were deployed on Railway during active data collection.

## Development

### Tech Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Python 3.11, Streamlit
- **LLM APIs**: OpenAI (GPT-4o, GPT-4o Mini), Anthropic (Claude Haiku, Claude Sonnet)
- **Infrastructure**: Docker, Docker Compose (local development; Railway for deployment)

### Environment Setup
```bash
# Backend
cd backend
python -m venv .venv
source .venv/Scripts/activate  # or .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

# Frontend
cd frontend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Author & Attribution
Master's thesis: Sindi Buklaji