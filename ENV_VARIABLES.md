# Environment Variables Reference

## Overview

This document lists all environment variables needed for deployment to Railway.

---

## Backend Environment Variables

Set these in the **backend-api** service on Railway.

### Required

#### `OPENAI_API_KEY`
- **Type**: String
- **Required**: Yes
- **Value**: Your OpenAI API key starting with `sk-`
- **Used for**: GPT-4o-mini chat completions, text-embedding-3-small embeddings
- **Example**: `sk-proj-abc123...xyz`
- **Get it from**: https://platform.openai.com/api-keys

#### `DATABASE_URL`
- **Type**: String (PostgreSQL connection string)
- **Required**: Yes
- **Value**: Provided by Railway PostgreSQL service
- **Format**: `postgresql://user:password@host:5432/dbname`
- **Example**: `postgresql://postgres:abc123@postgresml.railway.internal:5432/railway`
- **Get it from**: Railway PostgreSQL service → Variables tab → DATABASE_URL

#### `ADMIN_TOKEN`
- **Type**: String (32+ character random token)
- **Required**: Yes (in production)
- **Value**: Generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- **Used for**: Authenticating CSV export endpoints
- **Example**: `Drmhze6EPcv0fN_81Bj-nA`
- **Note**: Leave empty in development to skip authentication

### Optional (Defaults Shown)

#### `DEBUG`
- **Default**: `false`
- **Values**: `true` or `false`
- **Used for**: Enable debug endpoints at `/debug/...`
- **Production**: Set to `false`

#### `ALLOWED_ORIGINS`
- **Default**: `http://localhost:8501`
- **Type**: Comma-separated URLs
- **Used for**: CORS - which domains can call the API
- **Production**: Set to your frontend URL: `https://frontend-ui-<id>.railway.app`
- **Example**: `https://frontend-ui-abc123.railway.app`

#### `OPENAI_MODEL`
- **Default**: `gpt-4o-mini`
- **Type**: String
- **Used for**: Chat completions model
- **Note**: gpt-4o-mini is cost-effective for this use case

#### `OPENAI_EMBEDDING_MODEL`
- **Default**: `text-embedding-3-small`
- **Type**: String
- **Used for**: Creating embeddings for retrieval augmented generation

#### `MIN_TURNS`
- **Default**: `3`
- **Type**: Integer
- **Used for**: Minimum chat turns before allowing questionnaire
- **Study parameter**: Match your study design

#### `MAX_TURNS`
- **Default**: `5`
- **Type**: Integer
- **Used for**: Maximum chat turns before forcing questionnaire
- **Study parameter**: Match your study design

#### `TEMPERATURE`
- **Default**: `1.0`
- **Type**: Float (0.0 - 2.0)
- **Used for**: OpenAI response randomness
- **Note**: 1.0 = moderate randomness (recommended for personas)

#### `TOP_K_RETRIEVAL`
- **Default**: `3`
- **Type**: Integer
- **Used for**: Number of documents to retrieve for context

#### `RETRIEVAL_ENABLED`
- **Default**: `true`
- **Values**: `true` or `false`
- **Used for**: Enable retrieval augmented generation

#### `RETRIEVAL_USE_EMBEDDINGS`
- **Default**: `true`
- **Values**: `true` or `false`
- **Used for**: Use embeddings vs. keyword matching for retrieval

#### `RETRIEVAL_LOGGING_ENABLED`
- **Default**: `true`
- **Values**: `true` or `false`
- **Used for**: Log retrieval operations for reproducibility

---

## Frontend Environment Variables

Set these in the **frontend-ui** service on Railway.

### Required

#### `BACKEND_URL`
- **Type**: String (Full URL)
- **Required**: Yes
- **Value**: Public URL of backend service
- **Format**: `https://backend-api-<id>.railway.app`
- **Example**: `https://backend-api-abc123.railway.app`
- **Get it from**: backend-api service → Settings → Domain

### Optional (Streamlit Config)

#### `STREAMLIT_SERVER_HEADLESS`
- **Default**: `true`
- **Values**: `true` or `false`
- **Used for**: Run Streamlit without interactive shell
- **Production**: Keep `true`

#### `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION`
- **Default**: `true`
- **Values**: `true` or `false`
- **Used for**: Security - prevent cross-site request forgery
- **Production**: Keep `true`

---

## PostgreSQL (Database)

This is created automatically by Railway. You don't set variables, but Railway provides:

- **DATABASE_URL**: Copy this to backend service
- **PGHOST**: Database host
- **PGPORT**: Database port (5432)
- **PGUSER**: Database user
- **PGPASSWORD**: Database password
- **PGDATABASE**: Database name (default: `railway`)

**Note**: Use `DATABASE_URL` instead of individual vars for convenience.

---

## Complete Backend Setup (Copy-Paste)

Use this checklist when configuring the backend service on Railway:

```
OPENAI_API_KEY = sk-[paste-your-key-here]
DATABASE_URL = [copy from PostgreSQL service]
ADMIN_TOKEN = [generate-new-token]
DEBUG = false
ALLOWED_ORIGINS = https://frontend-ui-[your-id].railway.app
OPENAI_MODEL = gpt-4o-mini
OPENAI_EMBEDDING_MODEL = text-embedding-3-small
MIN_TURNS = 3
MAX_TURNS = 5
TEMPERATURE = 1.0
TOP_K_RETRIEVAL = 3
RETRIEVAL_ENABLED = true
RETRIEVAL_USE_EMBEDDINGS = true
RETRIEVAL_LOGGING_ENABLED = true
```

---

## Complete Frontend Setup (Copy-Paste)

Use this checklist when configuring the frontend service on Railway:

```
BACKEND_URL = https://backend-api-[your-id].railway.app
STREAMLIT_SERVER_HEADLESS = true
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION = true
```

---

## Generating ADMIN_TOKEN

Run this command locally:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Output example:
```
Drmhze6EPcv0fN_81Bj-nAvc5s3jGdB4Z6JqM6vQ5yE
```

Copy and paste this into the `ADMIN_TOKEN` field in Railway backend service.

---

## Testing Environment Variables

### Test Backend Connection

```bash
BACKEND="https://backend-api-[your-id].railway.app"

# Health check
curl "$BACKEND/health"

# Expected output:
# {"status":"ok"}
```

### Test Frontend Connection

```bash
FRONTEND="https://frontend-ui-[your-id].railway.app"

# Should load HTML
curl -I "$FRONTEND"

# Expected: 200 OK
```

### Test Admin Token

```bash
TOKEN="[your-ADMIN_TOKEN]"
BACKEND="https://backend-api-[your-id].railway.app"

# Should return CSV
curl -H "Authorization: Bearer $TOKEN" \
  "$BACKEND/export/participants.csv" \
  | head -c 100
```

---

## Security Best Practices

1. **OPENAI_API_KEY**
   - ✅ Keep secret - never commit to git
   - ✅ Set only in Railway (not in .env file)
   - ✅ Rotate if ever exposed

2. **ADMIN_TOKEN**
   - ✅ Generate strong random token
   - ✅ Set only in Railway (not in .env file)
   - ✅ Don't share with participants
   - ✅ Rotate periodically (between study cohorts)

3. **DATABASE_URL**
   - ✅ Keep secret - never commit to git
   - ✅ Let Railway manage (copy from service)
   - ✅ Don't share credentials publicly

4. **ALLOWED_ORIGINS**
   - ✅ Set to exact frontend URL
   - ✅ Don't use wildcard `*`
   - ✅ Update when moving to different domain

---

## Local Development vs. Production

### Local Development (.env file)

```
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./thesis_chatbot.db
ADMIN_TOKEN=  # (empty - no auth required)
DEBUG=true
ALLOWED_ORIGINS=http://localhost:8501
```

### Production (Railway Variables)

```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...@railway.internal:5432/railway
ADMIN_TOKEN=Drmhze6EPcv0fN_81Bj-nAvc5s3jGdB4Z6JqM6vQ5yE
DEBUG=false
ALLOWED_ORIGINS=https://frontend-ui-[id].railway.app
```

---

## Troubleshooting

### Backend won't start
- Check OPENAI_API_KEY is valid
- Check DATABASE_URL format and connectivity
- Check DEBUG is set to false in production

### Frontend shows "Backend connection refused"
- Check BACKEND_URL has `https://` (not `http://`)
- Check BACKEND_URL matches actual backend domain
- Verify ALLOWED_ORIGINS on backend includes frontend URL

### Exports fail with 401 error
- Check ADMIN_TOKEN is set correctly in backend
- Check header format: `Authorization: Bearer <TOKEN>`
- Verify token matches exactly (copy-paste check)

### Database errors
- Check DATABASE_URL format
- Verify PostgreSQL service is running (green ✓)
- Check if database needs migration: `alembic upgrade head`

---

## Contact & Support

- OpenAI API issues: https://platform.openai.com/account/api-keys
- Railway platform: https://railway.app/docs
- PostgreSQL issues: https://www.postgresql.org/docs/
