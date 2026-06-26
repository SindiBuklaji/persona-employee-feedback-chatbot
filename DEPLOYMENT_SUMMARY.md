# Railway Deployment - Summary of Changes

## Deliverables Provided

### 1. Documentation Files
✅ **DEPLOYMENT_PLAN.md** - High-level deployment overview
✅ **DEPLOY.md** - Detailed step-by-step Railway setup guide
✅ **TEST_CHECKLIST.md** - Complete testing protocol before launch
✅ **ENV_VARIABLES.md** - Environment variable reference guide
✅ **railway.json** - Optional Railway configuration file

### 2. Code Changes

#### Backend (`backend/app/`)

**config.py**
- Added `admin_token: str = ""` setting
- Allows environment variable `ADMIN_TOKEN` to be set at deployment

**routers/export.py**
- Added `verify_admin_token()` dependency
- Protects all 6 export endpoints:
  - `/export/participants.csv`
  - `/export/transcripts.csv`
  - `/export/questionnaires.csv`
  - `/export/honesty_codings.csv`
  - `/export/retrieval_logs.csv`
  - `/export/analysis_dataset.csv`
- Returns 401 Unauthorized if token missing/invalid
- Allows unprotected access in development (when `ADMIN_TOKEN` is empty)

**Dockerfile**
- Changed CMD to production mode: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- Removed `--reload` flag (development only)
- Adds automatic database migrations on startup
- Uses 4 uvicorn workers for better performance

**`.env.example`**
- Updated with production environment variable examples
- Clear documentation for local vs. Railway setup
- Includes admin token generation instructions

#### Frontend (`frontend/`)

**Dockerfile**
- Added Streamlit production configuration
- Sets `headless = true` (no interactive shell)
- Disables error details display
- Enables XSRF protection
- Uses `--client.toolbarMode=minimal` for cleaner UI

**`.env.example`**
- Updated with backend URL examples
- Includes Streamlit configuration options
- Clear comments for Railway URLs

---

## What Changed vs. What Stayed the Same

| Component | Changed? | Details |
|-----------|----------|---------|
| **Chat Logic** | ❌ No | Personas, RAG, persona assignment all unchanged |
| **Database Schema** | ❌ No | Same tables, migrations still work |
| **Vignette & Study Flow** | ❌ No | Participant experience is identical |
| **API Endpoints** | ✅ Some | Export endpoints now require `ADMIN_TOKEN` |
| **Backend Config** | ✅ Yes | Added `admin_token` setting |
| **Frontend Config** | ✅ Yes | Streamlit production settings added |
| **Deployment** | ✅ Yes | From Docker Compose → Railway |
| **Database** | ✅ Yes | From local Docker volume → Railway PostgreSQL |

---

## Files Modified

```
backend/app/
  ├── config.py ........................ ✏️ Added admin_token setting
  └── routers/
      └── export.py .................... ✏️ Added auth to 6 endpoints

backend/
  ├── Dockerfile ....................... ✏️ Production mode
  └── .env.example ..................... ✏️ Updated docs

frontend/
  ├── Dockerfile ....................... ✏️ Streamlit production config
  └── .env.example ..................... ✏️ Updated docs

Root project/
  ├── DEPLOY.md ........................ 📝 NEW - Step-by-step guide
  ├── DEPLOYMENT_PLAN.md .............. 📝 NEW - Overview
  ├── TEST_CHECKLIST.md ............... 📝 NEW - Testing protocol
  ├── ENV_VARIABLES.md ................ 📝 NEW - Variable reference
  ├── railway.json .................... 📝 NEW - Optional config
  └── DEPLOYMENT_SUMMARY.md ........... 📝 NEW - This file
```

---

## Next Steps

### Phase 1: Prepare Code (Today, ~30 min)

- [ ] Review changes in `config.py` and `export.py`
- [ ] Test locally that admin token authentication works
  ```bash
  # In backend directory
  python -m pytest backend/tests/  # if you have tests
  # Or manually test export endpoints with token
  ```
- [ ] Commit changes to git
  ```bash
  git add .
  git commit -m "feat: add admin token auth and production deployment config for Railway"
  git push origin main
  ```

### Phase 2: Deploy to Railway (Day 1, ~1-2 hours)

1. **Create Railway Account**
   - Sign up at railway.app (use GitHub login for easiest auth)

2. **Follow DEPLOY.md Step 1-2: Set up services**
   - Create project
   - Add PostgreSQL database
   - Copy DATABASE_URL

3. **Follow DEPLOY.md Step 3: Deploy Backend**
   - Create backend service from GitHub
   - Set environment variables:
     - `OPENAI_API_KEY=sk-...`
     - `DATABASE_URL=postgresql://...`
     - `ADMIN_TOKEN=<generate-new>`
     - `DEBUG=false`
     - `ALLOWED_ORIGINS=https://frontend-ui-[id].railway.app` (placeholder, update later)
   - Wait for deployment (5-10 min)
   - Copy backend URL

4. **Follow DEPLOY.md Step 4: Deploy Frontend**
   - Create frontend service from GitHub
   - Set environment variables:
     - `BACKEND_URL=https://backend-api-[id].railway.app` (use URL from step 3)
   - Wait for deployment (5-10 min)
   - Copy frontend URL
   - **UPDATE backend `ALLOWED_ORIGINS`** with frontend URL now that you know it

5. **Follow DEPLOY.md Step 5-6: Testing**
   - Run health checks
   - Test full participant flow 2x
   - Verify persona assignment
   - Test admin exports

### Phase 3: Pre-Launch Verification (Day 2, ~1-2 hours)

- [ ] Complete TEST_CHECKLIST.md thoroughly
  - Full participant flow testing (2x, different personas)
  - Admin token authentication
  - Browser compatibility testing
  - Error handling
  - Data verification in CSV exports

- [ ] Final checks:
  - [ ] No console errors in frontend
  - [ ] Chat responses feel natural
  - [ ] Persona assignment is ~50/50 warm vs competent
  - [ ] All 6 CSV exports work with token
  - [ ] Database contains correct test data

### Phase 4: Launch (Day 3, Ready!)

- [ ] Share frontend URL with participants
- [ ] Begin recruitment
- [ ] Monitor daily for errors
- [ ] Export data weekly for backup

---

## Generated ADMIN_TOKEN

When you deploy, you'll need to generate a token:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output**:
```
Drmhze6EPcv0fN_81Bj-nAvc5s3jGdB4Z6JqM6vQ5yE
```

Paste this into Railway backend environment: `ADMIN_TOKEN=Drmhze6EPcv0fN_81Bj-nAvc5s3jGdB4Z6JqM6vQ5yE`

---

## Cost Estimate (Railway)

**Free Tier**: $5/month provided free to all users
**Usage-based pricing** after that:

| Component | Estimated Cost | Notes |
|-----------|----------------|-------|
| Backend (FastAPI) | $0-5/month | ~100-1000 requests/day |
| Frontend (Streamlit) | $0-5/month | Minimal CPU usage |
| PostgreSQL | $0-5/month | Data grows slowly |
| **Total** | **~$5-15/month** | Well within free tier for 2-month study |

You can monitor usage in Railway dashboard.

---

## Deployment Architecture (Final)

```
Participants (Browser)
        ↓
   railway.app
        ↓
┌───────────────────────────────────┐
│   Railway Project                 │
│  ┌──────────────────────────────┐ │
│  │ Streamlit Frontend (8501)    │ │
│  │ https://frontend-ui-*.*.app  │ │
│  └────────────┬─────────────────┘ │
│               │                    │
│  ┌────────────▼─────────────────┐ │
│  │ FastAPI Backend (8000)       │ │
│  │ https://backend-api-*.*.app  │ │
│  │ - /session/start             │ │
│  │ - /chat/send                 │ │
│  │ - /questionnaire/submit      │ │
│  │ - /export/* (requires token) │ │
│  └────────────┬─────────────────┘ │
│               │                    │
│  ┌────────────▼─────────────────┐ │
│  │ PostgreSQL (Managed)         │ │
│  │ Participants, Messages, etc. │ │
│  └──────────────────────────────┘ │
└───────────────────────────────────┘
        ↓
    OpenAI API
    (GPT-4o-mini, embeddings)
```

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| **Backend won't start** | Check OPENAI_API_KEY, DATABASE_URL format, logs |
| **Frontend shows connection error** | Check BACKEND_URL, ensure backend is running, check ALLOWED_ORIGINS |
| **Export endpoints return 401** | Verify ADMIN_TOKEN set correctly, check header format |
| **Database errors** | Verify DATABASE_URL, wait for PostgreSQL to initialize |
| **Persona assignment broken** | Restart backend service, check randomization.py exists |
| **Slow responses** | Check OpenAI API rate limits, monitor Railway CPU usage |
| **Participant sees database errors** | Check logs, verify migrations ran on startup |

For detailed troubleshooting, see DEPLOY.md Troubleshooting section.

---

## Key Points for Research Integrity

✅ **Randomization maintained**: 50/50 warm vs competent assignment unchanged
✅ **Persona faithfulness**: Same persona prompts, just hosted on Railway
✅ **Data privacy**: PostgreSQL is secure, ADMIN_TOKEN protects exports
✅ **Reproducibility**: All retrieval logs exported with corpus version
✅ **Auditability**: CSV exports include participant IDs, conditions, timestamps

---

## Support During Study

If issues occur during the study:

1. **Check Railway logs first**
   - Log into Railway dashboard
   - View backend/frontend service logs
   - Look for recent errors

2. **Verify services are running**
   - All 3 services should show green ✓
   - PostgreSQL should be healthy

3. **Quick fix: Redeploy**
   - Push fix to GitHub
   - Railway auto-redeploys (if enabled)
   - Or manually restart service in Railway dashboard

4. **Export data immediately**
   - If issues are severe, export all CSVs with admin token
   - Keep local backup

5. **Worst case: Rollback**
   - Stop affected service
   - Fix code locally
   - Redeploy
   - Database persists across deployments

---

## After Study (Data Archival)

Once all participants complete:

1. **Final data export**
   ```bash
   # Use ADMIN_TOKEN to download all CSVs
   # Save to local research storage
   ```

2. **Database backup**
   - Railway → PostgreSQL service → Create Backup
   - Download backup file

3. **Shut down services** (stop incurring costs)
   - Delete backend service
   - Delete frontend service
   - Delete PostgreSQL service
   - Keep all exported data archived

4. **Data analysis**
   - Use analysis_dataset.csv for regression models
   - Use transcripts.csv + questionnaires.csv for detailed analysis
   - Use retrieval_logs.csv to validate RAG reproducibility

---

## Questions?

Refer to:
- **"How do I deploy?"** → See DEPLOY.md
- **"What environment variables?"** → See ENV_VARIABLES.md
- **"How do I test?"** → See TEST_CHECKLIST.md
- **"Big picture view?"** → See DEPLOYMENT_PLAN.md

---

**Created**: June 26, 2026
**Status**: ✅ Ready for deployment
**Estimated time to launch**: 2-3 days
