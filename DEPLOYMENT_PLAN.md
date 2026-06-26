# Railway Deployment Plan

## Overview
Deploy the Persona-Employee-Feedback-Chatbot to Railway for a 2-month thesis study. The deployment includes:
- **FastAPI Backend** (Python 3.11) on Railway
- **Streamlit Frontend** (Python 3.11) on Railway  
- **PostgreSQL Database** (managed by Railway)
- **OpenAI API** integration for chat completions and embeddings

## Architecture

```
Participants
    ↓
[Railway URL] → Streamlit Frontend (8501)
                    ↓
                FastAPI Backend (8000)
                    ↓
                PostgreSQL (Railway managed)
                    ↓
                OpenAI API
```

## Key Changes from Local Docker Setup

| Component | Local | Production |
|-----------|-------|-----------|
| **PostgreSQL** | Local Docker volume | Railway managed database |
| **Backend PORT** | 8000 (reload mode) | 8000 (production mode, no reload) |
| **Frontend PORT** | 8501 (interactive) | 8501 (headless mode) |
| **DEBUG** | true | false |
| **CORS Origins** | localhost:8501 | Railway frontend URL |
| **Admin Endpoints** | Unprotected | Require ADMIN_TOKEN header |
| **Environment Variables** | .env file | Railway environment variables |

## Files Changed

### 1. Backend Configuration (`backend/app/config.py`)
- Add `admin_token` setting (required, generated at deployment)
- Update `cors_origins` to accept Railway frontend URL

### 2. Backend Dockerfiles
- `backend/Dockerfile` → Production mode (no --reload)
- `frontend/Dockerfile` → Headless mode + optimized config

### 3. Export Router (`backend/app/routers/export.py`)
- Add ADMIN_TOKEN authentication to all export endpoints
- Return 401 if token missing or invalid

### 4. Streamlit App (`frontend/streamlit_app.py`)
- Update BACKEND_URL to use environment variable
- Hide debug UI in production (when DEBUG=false)

### 5. New Deployment Docs
- `DEPLOY.md` - Step-by-step Railway setup
- `.env.example` - Template for environment variables
- `railway.json` - Optional Railway configuration

## Environment Variables (Production)

```
# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@host:5432/thesis_chatbot
ADMIN_TOKEN=<random-32-char-token>

# Optional (defaults shown)
DEBUG=false
RETRIEVAL_ENABLED=true
RETRIEVAL_USE_EMBEDDINGS=true
RETRIEVAL_LOGGING_ENABLED=true
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
MIN_TURNS=3
MAX_TURNS=5
TEMPERATURE=1.0
TOP_K_RETRIEVAL=3
ALLOWED_ORIGINS=https://your-frontend-url.railway.app
```

## Deployment Steps Summary

1. **Railway Setup**
   - Create Railway account (railway.app)
   - Create project for the chatbot
   - Create PostgreSQL database service
   - Set up environment variables

2. **Code Changes**
   - Implement ADMIN_TOKEN authentication
   - Update Dockerfiles for production
   - Commit changes to git

3. **Deploy Services**
   - Deploy backend (FastAPI)
   - Deploy frontend (Streamlit)
   - Verify health checks

4. **Data & Migration**
   - Run Alembic migrations on startup
   - Verify database schema

5. **Testing**
   - Test participant flow (consent → vignette → chat → questionnaire)
   - Test persona randomization (50/50 warm vs competent)
   - Test CSV exports (with ADMIN_TOKEN)
   - Monitor logs for errors

6. **Share Participant Link**
   - Get frontend public URL from Railway
   - Share with research participants
   - Monitor for issues during study

## Timeline

- **Immediate**: Implement code changes (1-2 hours)
- **Day 1**: Deploy to Railway & test (1-2 hours)
- **Day 2**: Full participant flow testing (1-2 hours)
- **Day 3**: Ready for participant recruitment

## Rollback Plan

If issues occur:
1. Stop services on Railway (keeps database)
2. Fix code locally & test
3. Redeploy services
4. Database persists across deployments

## Monitoring

Post-deployment:
- Check Railway logs daily for errors
- Export data weekly (CSV exports)
- Monitor OpenAI API usage & costs
- Verify participant counts and conditions are 50/50

## Support & Maintenance

**During Study (2 months)**:
- Daily: Check logs & participant count
- Weekly: Export data for backup
- As-needed: Fix bugs, optimize performance

**After Study**:
- Export all data (transcripts, questionnaires, responses)
- Back up database
- Shut down services to stop incurring costs
- Archive data for analysis

---

See `DEPLOY.md` for detailed Railway setup instructions.
