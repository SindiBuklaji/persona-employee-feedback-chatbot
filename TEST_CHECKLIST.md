# Pre-Participant-Launch Test Checklist

Complete this checklist BEFORE sharing the study link with participants.

## Infrastructure Verification

- [ ] Railway backend service is **Running** (green ✓ status)
- [ ] Railway frontend service is **Running** (green ✓ status)
- [ ] Railway PostgreSQL database is **Running** (green ✓ status)
- [ ] All services show **healthy** status in Railway dashboard

## Health Checks

- [ ] Backend health endpoint responds:
  ```bash
  curl https://backend-api-<id>.railway.app/health
  # Expected: {"status":"ok"}
  ```

- [ ] Frontend loads without errors in browser:
  - [ ] No CORS errors in browser console
  - [ ] No "Backend connection refused" messages
  - [ ] Styling loads correctly

## Full Participant Flow (Test 1: Warm Persona)

Use your browser's private/incognito window to simulate a participant.

### Consent Screen
- [ ] Consent page displays correctly
- [ ] Text is readable and centered
- [ ] "I consent" button is visible and clickable
- [ ] Button is enabled (not grayed out)

### Click "I consent"
- [ ] Page transitions to Vignette
- [ ] No error messages appear
- [ ] URL updates (if using session routing)

### Vignette Screen
- [ ] Scenario title is visible
- [ ] Scenario text is readable (about workload/coordination issues)
- [ ] "Continue to Chat" button is visible

### Click "Continue to Chat"
- [ ] Chat interface loads
- [ ] Opening message appears from Assistant
- [ ] **Tone check**: Message should be warm/supportive (friendly, understanding)
  - Look for words like "I understand", "let's work through", "together"
  - Avoid overly analytical tone
- [ ] Chat input box is enabled and ready

### Chat Phase (minimum 3 turns)
- [ ] Turn 1: Send a message describing your workload issue
  - [ ] Assistant responds with empathetic tone
  - [ ] Response asks about the impact on your work
  - [ ] Response matches warm persona
  
- [ ] Turn 2: Send response to follow-up
  - [ ] Assistant acknowledges your response
  - [ ] Next message asks about causes/contributing factors
  - [ ] Consistent warm tone
  
- [ ] Turn 3: Send response about causes
  - [ ] Assistant validates your perspective
  - [ ] Asks about potential improvements
  - [ ] Maintains supportive tone
  
- [ ] Turn 4+: Continue chat until options appear
  - [ ] Chat feels natural and supportive
  - [ ] Message word counts seem reasonable (not too long/short)
  - [ ] No repeated prompts or loops

### Complete Chat
- [ ] "Move to Questionnaire" button appears after min 3 turns
- [ ] Button becomes enabled
- [ ] Click button

### Questionnaire Screen
- [ ] 6 perception items visible (3 warmth, 3 structured/direct)
  - [ ] "My assistant was friendly" (1-7 scale)
  - [ ] "My assistant was understanding" (1-7 scale)
  - [ ] "I felt comfortable with my assistant" (1-7 scale)
  - [ ] "My assistant was direct" (1-7 scale)
  - [ ] "My assistant was professional" (1-7 scale)
  - [ ] "My assistant was task-focused" (1-7 scale)

- [ ] 5 psychological safety items visible
  - All labeled with 1-7 scale
  
- [ ] 4 openness/honesty items visible
  - All labeled with 1-7 scale

- [ ] Demographics section (AI experience, work experience, age, gender, industry, role)
  - [ ] All fields have appropriate input types (text, dropdown, number)

- [ ] "Submit" button at bottom
- [ ] All required fields show clear labels

### Fill Questionnaire
- [ ] Can select values for all items (click to rate)
- [ ] Can fill text fields for demographics
- [ ] No validation errors for valid entries
- [ ] Submit button is enabled

### Submit Questionnaire
- [ ] Page transitions to "Thank You"
- [ ] Thank you message displays
- [ ] Displays psychological safety score (should be ~3.5-4 if rated mid-range)
- [ ] No errors in browser console

---

## Full Participant Flow (Test 2: Competent Persona)

Repeat the exact same flow in a NEW incognito window to test the **other** persona.

### Opening Message Tone Check
- [ ] **Tone check**: Message should be structured/competent (analytical, professional)
  - Look for words like "let's analyze", "key factors", "clarify", "approach"
  - Avoid overly warm/empathetic language

### Chat Phase Tone Check
- [ ] Turn 1 response is analytical and structured
- [ ] Turn 2 response focuses on root causes
- [ ] Turn 3 response suggests systematic improvements
- [ ] Tone remains professional throughout

### After Questionnaire
- [ ] Same thank you page appears
- [ ] Psychological safety score displays

---

## Persona Assignment Verification

Run at least 3 tests (clean sessions) and check the opening message tone:

| Test # | Expected Tone | Actual Tone | Correct? |
|--------|---------------|------------|----------|
| 1      | Warm OR Competent | _____ | ☐ |
| 2      | Warm OR Competent | _____ | ☐ |
| 3      | Warm OR Competent | _____ | ☐ |

**Check**: Approximately 50/50 split between warm and competent (expect ~1-2 of each type in 3 tests)

---

## Admin Export Testing

### Test Admin Token Authentication

Generate a test token:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output
```

Set it in Railway backend environment variables as `ADMIN_TOKEN`.

### Test Export Endpoints

```bash
TOKEN="<your-test-token>"
BACKEND="https://backend-api-<id>.railway.app"

# Test 1: Valid token should return CSV
curl -H "Authorization: Bearer $TOKEN" \
  "$BACKEND/export/participants.csv" \
  -o participants.csv && \
  echo "✓ Export succeeded" || echo "✗ Export failed"

# Test 2: Invalid token should return 401
curl -H "Authorization: Bearer invalid-token" \
  "$BACKEND/export/participants.csv" \
  -I && echo "✗ Should have failed" || echo "✓ Correctly rejected"

# Test 3: No token should return 401
curl "$BACKEND/export/participants.csv" \
  -I && echo "✗ Should have failed" || echo "✓ Correctly rejected"

# Test all export endpoints
for csv in participants transcripts questionnaires analysis_dataset retrieval_logs honesty_codings; do
  curl -H "Authorization: Bearer $TOKEN" \
    "$BACKEND/export/${csv}.csv" \
    > "${csv}.csv" && \
    echo "✓ $csv.csv" || \
    echo "✗ $csv.csv failed"
done
```

- [ ] Valid token returns CSV data
- [ ] Invalid token returns 401 Unauthorized
- [ ] No token returns 401 Unauthorized
- [ ] All export endpoints return valid CSV files

---

## Browser & Network Testing

- [ ] Test on Chrome (most common)
- [ ] Test on Firefox (desktop)
- [ ] Test on mobile Safari (iPad)
- [ ] Test on Chrome Android (mobile)

For each browser:
- [ ] No console errors
- [ ] No console warnings about CORS
- [ ] Chat works smoothly
- [ ] Buttons respond immediately
- [ ] Text is readable and properly formatted

---

## Performance & Load

- [ ] Chat responses appear within 10 seconds
- [ ] Multiple chat turns don't slow down the interface
- [ ] Questionnaire page loads without lag
- [ ] Export endpoints respond within 30 seconds

---

## Error Handling

### Simulate Errors

1. **Temporarily stop backend service** in Railway
   - [ ] Frontend shows error message (not blank page)
   - [ ] Error message is user-friendly
   - [ ] Restart backend service

2. **Send malformed chat request**
   - [ ] Backend returns 400 error
   - [ ] Frontend doesn't crash
   - [ ] User can try again

3. **Fill questionnaire incompletely**
   - [ ] Submit button disabled OR shows validation error
   - [ ] Can fix and resubmit
   - [ ] Clear which fields are required

---

## Data Verification

After completing at least 2 full test flows:

### Check Database Data

```bash
TOKEN="<your-test-token>"
BACKEND="https://backend-api-<id>.railway.app"

# Export and inspect participants CSV
curl -H "Authorization: Bearer $TOKEN" \
  "$BACKEND/export/participants.csv" \
  | head -5
```

Expected CSV headers present:
- [ ] participant_id
- [ ] condition (should be "warm" or "competent")
- [ ] completed_task
- [ ] number_user_turns
- [ ] total_user_word_count
- [ ] started_at
- [ ] completed_at

Verify data:
- [ ] Both "warm" and "competent" conditions appear in data
- [ ] completed_task is 1 (true) for completed sessions
- [ ] number_user_turns >= 3
- [ ] timestamps are reasonable

---

## Final Safety Checks

### Code Review
- [ ] No hardcoded passwords or API keys in code
- [ ] ADMIN_TOKEN is only set via environment variable
- [ ] No debug endpoints enabled in production (DEBUG=false)
- [ ] No test data or sensitive comments visible

### Security Checks
- [ ] Export endpoints require ADMIN_TOKEN
- [ ] CORS is limited to frontend domain only
- [ ] HTTPS enforced (all Railway URLs are https://)
- [ ] No verbose error messages in production (users see generic errors)

### Participant Privacy
- [ ] No console.log of sensitive participant data
- [ ] No participant IDs shown to other participants
- [ ] Each session is isolated (can't see others' conversations)
- [ ] Session data properly cleared between participants

---

## Production Readiness Sign-Off

- [ ] All tests above passed ✓
- [ ] No critical errors in logs
- [ ] Response times are acceptable
- [ ] Persona assignment is 50/50
- [ ] Admin export works with token
- [ ] Database is healthy and responding
- [ ] Frontend URL is shareable and user-friendly

**Ready to launch?** ☐ YES ☐ NO

If NO, list issues:
```
1. 
2. 
3. 
```

---

## Monitoring After Launch

### Daily (During Study)
- [ ] Check Railway dashboard for errors
- [ ] Verify services are running (green ✓)
- [ ] Spot-check logs for warnings

### Weekly
- [ ] Count participants enrolled
- [ ] Check condition distribution (should be ~50/50)
- [ ] Export data for backup
- [ ] Review any error patterns in logs

### On Demand
- [ ] Test with new participant to verify flow still works
- [ ] Monitor OpenAI API usage
- [ ] Check database storage (should grow slowly)

---

**Completion Date**: ______________

**Tester Name**: ______________

**Issues Found**: ☐ None ☐ Minor (list above) ☐ Critical (do not launch)
