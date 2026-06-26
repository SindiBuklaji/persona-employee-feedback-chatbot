# Railway Deployment Guide

## Prerequisites

- GitHub repository with the code
- Railway account (free tier available at railway.app)
- OpenAI API key (for GPT-4o-mini & embeddings)
- Git installed locally

## Step 1: Prepare Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub account (easiest auth method)
3. Create a new project: **New Project** → **Deploy from GitHub**
4. Select your persona-feedback-chatbot repository
5. Authorize Railway to access your GitHub account

## Step 2: Add PostgreSQL Database

1. In your Railway project, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway will create a postgres service with automatic backups
4. Copy the `DATABASE_URL` from the PostgreSQL settings (under Variables tab)
5. You'll use this in the backend service setup

## Step 3: Deploy Backend Service

### 3a. Create Backend Service from GitHub

1. Click **+ New** → **GitHub Repo**
2. Select the same repository
3. Set the service name to `backend-api`
4. In the **Deploy** tab, set:
   - **Root Directory**: `backend`
   - **Dockerfile**: Leave blank (auto-detects from backend/Dockerfile)
   - **PORT**: 8000

### 3b. Configure Environment Variables

In the backend service's **Variables** tab, add:

```
# OpenAI API
OPENAI_API_KEY=sk-<your-actual-key>
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Database (copy from PostgreSQL service)
DATABASE_URL=postgresql://...@<host>:5432/railway

# Admin Token (generate 32-character random token)
# Can use: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
ADMIN_TOKEN=<generate-and-paste-here>

# Feature flags
DEBUG=false
RETRIEVAL_ENABLED=true
RETRIEVAL_USE_EMBEDDINGS=true
RETRIEVAL_LOGGING_ENABLED=true

# Study parameters
MIN_TURNS=3
MAX_TURNS=5
TEMPERATURE=1.0
TOP_K_RETRIEVAL=3
ALLOWED_ORIGINS=https://<your-frontend-url>.railway.app

# Optional: Model overrides (use defaults if not needed)
# OPENAI_MODEL=gpt-4o-mini
# OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

**⚠️ Important**: Generate a strong ADMIN_TOKEN:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3c. Wait for Backend to Deploy

- Railway will build the Docker image and deploy
- Check the **Deploy** tab for progress
- Once green ✓, the backend is live at `https://backend-api-<random>.railway.app`
- Test health: `curl https://backend-api-<random>.railway.app/health`

### 3d. Get Backend URL

- Copy the backend service's public URL from the **Settings** → **Domain**
- You'll use this in the frontend service

## Step 4: Deploy Frontend Service

### 4a. Create Frontend Service from GitHub

1. Click **+ New** → **GitHub Repo**
2. Select the same repository
3. Set the service name to `frontend-ui`
4. In the **Deploy** tab, set:
   - **Root Directory**: `frontend`
   - **Dockerfile**: Leave blank (auto-detects from frontend/Dockerfile)
   - **PORT**: 8501

### 4b. Configure Environment Variables

In the frontend service's **Variables** tab, add:

```
# Backend URL (copy from backend service)
BACKEND_URL=https://backend-api-<random>.railway.app

# For Streamlit config
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

### 4c. Wait for Frontend to Deploy

- Railway will build the Docker image and deploy
- Once green ✓, the frontend is live at `https://frontend-ui-<random>.railway.app`
- This is your **participant study link** 🎉

## Step 5: Test the Deployment

### 5a. Quick Health Check

```bash
# Test backend
curl https://backend-api-<random>.railway.app/health

# Test frontend (should load HTML)
curl -I https://frontend-ui-<random>.railway.app
```

### 5b. Full Participant Flow Test

1. Open frontend URL in browser
2. **Consent Screen**: Click "I consent"
3. **Vignette Screen**: Read the scenario
4. **Chat Phase**: 
   - Ask 1-2 questions (3-5 turns required)
   - Verify persona tone (warm vs structured)
5. **Questionnaire**: Fill in all 6 perception items
6. **Thank You**: See completion message

### 5c. Test CSV Exports (Admin Only)

**Generate ADMIN_TOKEN header:**
```bash
TOKEN="<your-ADMIN_TOKEN>"

# Test each export endpoint
curl -H "Authorization: Bearer $TOKEN" \
  "https://backend-api-<random>.railway.app/export/participants.csv"

curl -H "Authorization: Bearer $TOKEN" \
  "https://backend-api-<random>.railway.app/export/transcripts.csv"

curl -H "Authorization: Bearer $TOKEN" \
  "https://backend-api-<random>.railway.app/export/questionnaires.csv"

curl -H "Authorization: Bearer $TOKEN" \
  "https://backend-api-<random>.railway.app/export/analysis_dataset.csv"

curl -H "Authorization: Bearer $TOKEN" \
  "https://backend-api-<random>.railway.app/export/retrieval_logs.csv"
```

### 5d. Verify Persona Assignment

Test 2-3 times to confirm 50/50 warm vs competent:
- Check opening message tone
- Check follow-up responses

## Step 6: Share Participant Link

Your public study link is:
```
https://frontend-ui-<random>.railway.app
```

Share this with research participants. They do NOT need the backend or admin token.

## Monitoring & Maintenance

### Daily During Study

1. Check Railway dashboard for errors
2. Monitor deployed services status
3. Check backend logs for API errors

**View logs:**
- Click backend service → **Logs** tab
- Click frontend service → **Logs** tab
- Filter for errors/warnings

### Weekly Export Backup

Keep a local backup of data during the study:

```bash
TOKEN="<your-ADMIN_TOKEN>"
BACKEND_URL="https://backend-api-<random>.railway.app"

# Create backup directory
mkdir -p ./thesis_data_backups/$(date +%Y-%m-%d)

# Export all CSVs
for csv in participants transcripts questionnaires analysis_dataset retrieval_logs honesty_codings; do
  curl -H "Authorization: Bearer $TOKEN" \
    "$BACKEND_URL/export/${csv}.csv" \
    > "./thesis_data_backups/$(date +%Y-%m-%d)/${csv}.csv"
done

echo "Backup completed at ./thesis_data_backups/$(date +%Y-%m-%d)/"
```

### Monitor OpenAI API Costs

1. Go to [platform.openai.com](https://platform.openai.com)
2. Check **Billing** → **Usage** to track API costs
3. Set alerts if needed (Usage limits in Settings)

## Troubleshooting

### Frontend shows "Connection refused"
- ✅ Check backend BACKEND_URL is correct (including https://)
- ✅ Verify backend service is running (green ✓ in Railway)
- ✅ Check backend logs for startup errors

### Backend won't start
- ✅ Check `DATABASE_URL` format: `postgresql://user:pass@host:5432/dbname`
- ✅ Verify PostgreSQL service is running
- ✅ Check `OPENAI_API_KEY` is valid
- ✅ Check Docker build logs in Railway

### Database connection timeout
- ✅ Verify PostgreSQL service is healthy (green ✓)
- ✅ Check `DATABASE_URL` matches PostgreSQL credentials
- ✅ Wait 1-2 minutes for database to fully initialize

### 50/50 persona assignment not working
- ✅ Check `backend/app/services/randomization.py` is deployed
- ✅ Restart backend service (re-deploy)
- ✅ Check logs for randomization errors

### Admin token not working for exports
- ✅ Verify header format: `Authorization: Bearer <TOKEN>`
- ✅ Check token matches `ADMIN_TOKEN` env var (case-sensitive)
- ✅ Restart backend after changing `ADMIN_TOKEN`

## After the Study (Data Archival)

### Step 1: Final Data Export

```bash
TOKEN="<your-ADMIN_TOKEN>"
BACKEND_URL="https://backend-api-<random>.railway.app"

mkdir -p ./thesis_data_final_export
for csv in participants transcripts questionnaires analysis_dataset retrieval_logs honesty_codings; do
  curl -H "Authorization: Bearer $TOKEN" \
    "$BACKEND_URL/export/${csv}.csv" \
    > "./thesis_data_final_export/${csv}.csv"
done
```

### Step 2: Backup Database

In Railway PostgreSQL settings:
1. Click **Create Backup** button
2. Railway creates a snapshot you can download

### Step 3: Shut Down Services

To stop incurring Railway costs after the study:

1. Go to each service (backend, frontend, PostgreSQL)
2. Click **Settings** → **Delete**
3. Confirm deletion

**Note**: Railway charges by usage (free tier generous), but you can stop services to avoid any charges.

### Step 4: Archive Data

Keep the exported CSVs and PostgreSQL backup in:
- Local machine backup
- Cloud storage (Google Drive, Dropbox, etc.)
- University research storage

## Support & Debugging

**Check Railway status:**
- https://status.railway.app

**Get help:**
- Railway docs: https://docs.railway.app
- Project logs available in Railway dashboard

**Common questions:**
- Q: How long can I keep the study running?
  A: As long as you need. Railway billing is usage-based.

- Q: Can I update the code after deployment?
  A: Yes, push to GitHub and Railway auto-redeploys (disable this in service settings if needed).

- Q: How do I add participants?
  A: Just share the frontend URL. No participant list management needed.

- Q: What if I need to change the vignette?
  A: Update `backend/app/data/vignette.py`, push to GitHub, Railway redeploys automatically.

---

**Next**: See DEPLOYMENT_PLAN.md for overview, and check the TEST_CHECKLIST below before sharing the participant link.
