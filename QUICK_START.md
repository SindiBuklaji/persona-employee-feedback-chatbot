# Railway Deployment - Quick Start (TL;DR)

## 5-Minute Overview

You have a research chatbot. You want to deploy it to Railway so participants can access it via a public URL.

**Time to deploy**: ~2-3 days
**Cost**: $5-15/month (or free if under Railway's $5 credit)

---

## Checklist

### Before Deploying (Today)

- [ ] Push code changes to GitHub
  ```bash
  git add .
  git commit -m "Add Railway deployment config and admin token auth"
  git push origin main
  ```

### Deploy on Railway (Day 1)

Follow **DEPLOY.md** step-by-step:

1. Create Railway account at railway.app
2. Create PostgreSQL database → Copy `DATABASE_URL`
3. Deploy backend service
   - Set `OPENAI_API_KEY`, `DATABASE_URL`, `ADMIN_TOKEN`, `DEBUG=false`
   - Copy backend URL when done
4. Deploy frontend service
   - Set `BACKEND_URL` (from step 3)
5. Go back and update backend `ALLOWED_ORIGINS` to frontend URL

### Test Before Launch (Day 2)

Follow **TEST_CHECKLIST.md**:
- Test full participant flow (2x)
- Test persona assignment (should be ~50/50)
- Test admin exports with token
- Check for errors

### Launch (Day 3)

Share frontend URL with participants. Done! 🎉

---

## Key URLs

| Service | URL Pattern |
|---------|------------|
| **Frontend (Share this with participants!)** | `https://frontend-ui-[random].railway.app` |
| **Backend API** | `https://backend-api-[random].railway.app` |
| **Admin Dashboard** | `https://dashboard.railway.app` |

---

## Key Variables

### Backend (`ADMIN_TOKEN` must be unique!)

```
OPENAI_API_KEY=sk-...         [your OpenAI key]
DATABASE_URL=postgresql://... [copy from Railway PostgreSQL]
ADMIN_TOKEN=<generate>        [run: python3 -c "import secrets; print(secrets.token_urlsafe(32))"]
DEBUG=false
ALLOWED_ORIGINS=https://frontend-ui-[id].railway.app
```

### Frontend

```
BACKEND_URL=https://backend-api-[id].railway.app
```

---

## Generate ADMIN_TOKEN

Run this once:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy output → paste into Railway backend `ADMIN_TOKEN`

---

## Test Admin Exports

```bash
TOKEN="<your-admin-token>"
BACKEND="https://backend-api-[id].railway.app"

curl -H "Authorization: Bearer $TOKEN" \
  "$BACKEND/export/participants.csv" \
  -o participants.csv
```

If you get a CSV → ✅ Works!
If you get 401 → ❌ Check token

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Frontend: "Connection refused" | Check `BACKEND_URL`, restart backend service |
| Backend: Won't start | Check `OPENAI_API_KEY`, `DATABASE_URL`, view logs |
| Exports: 401 error | Verify `ADMIN_TOKEN`, check header format |
| Database: Connection error | Wait 2 min for PostgreSQL, check `DATABASE_URL` |
| Persona: All warm (or all competent) | Restart backend service |

---

## Support

- **Full guide**: DEPLOY.md
- **All variables**: ENV_VARIABLES.md
- **Test protocol**: TEST_CHECKLIST.md
- **Architecture**: DEPLOYMENT_PLAN.md

---

## Timeline

```
Day 0: Code changes ✅ (you are here)
Day 1: Deploy to Railway (follow DEPLOY.md)
Day 2: Test (follow TEST_CHECKLIST.md)
Day 3: Launch! Share link with participants
```

---

**Ready?** → Open **DEPLOY.md** and follow Step 1.
