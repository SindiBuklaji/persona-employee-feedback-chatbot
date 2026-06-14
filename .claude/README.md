# Project Plans & Documentation

This directory contains comprehensive planning documents for the **Persona-Employee-Feedback-Chatbot** thesis project.

## Files

### 1. `master-implementation-plan.md` ⭐ START HERE
**Complete roadmap for development, deployment, and data analysis**

Contains:
- Project overview and success criteria
- Full database schema (5 tables, 50+ columns)
- When each field is set during the chat flow
- Step-by-step implementation phases (5 phases, 18 tasks)
- Azure deployment instructions with exact CLI commands
- Data export formats and analysis workflows
- Testing checklist
- 10-day timeline to launch

**Use this when**: You need to know what to build, how it all connects, or how to deploy to Azure

---

### 2. `temporal-booping-gadget.md`
**Original phase-based implementation plan**

Contains:
- Phase 1: Critical Fixes (blinding, model names, opening message persistence)
- Phase 2: Data Integrity (honesty constraints, dropout tracking)
- Phase 3: Security & Privacy (export authentication)
- Phase 4: UX Improvements (loading spinners, UI polish)
- Phase 5: Pre-Launch Verification (test checklist)

**Use this when**: You're implementing specific phases or need a checklist

---

### 3. `logging-specification.md`
**Detailed logging & metrics specification**

Contains:
- Every variable that will be collected for data analysis
- Session-level logging (when session starts/ends)
- Turn-level logging (per-message metrics)
- Engagement metrics (word counts, response times, trends)
- Feedback honesty dimensions (criticality, specificity, riskiness)
- Psychological safety & manipulation checks
- Control variables & covariates
- Export CSV schemas (column lists)
- Priority levels (HIGH, MEDIUM, LOWER)

**Use this when**: Designing logging, understanding what data is collected, or setting up exports

---

## Current Status

### ✅ Completed
- Database models updated (all timestamp columns, metrics fields)
- All routers refactored to use new column names
- Schemas updated for consistency
- Unique constraint added to honesty codings
- Session timestamp tracking in place
- Chat and questionnaire routers updated

### ⏳ In Progress
- Message metrics (character_count, sentence_count, response_latency_seconds)
- Separate turn indexing (user vs assistant)
- Template metrics calculations in metrics.py

### 📋 Not Started
- Frontend timestamp logging
- Export endpoints (5 CSVs)
- Azure deployment setup
- API key authentication

---

## Quick Reference

### Database Schema Summary
| Table | Rows | Purpose |
|---|---|---|
| `participants` | 1 per participant | Session metadata, timestamps, completion |
| `messages` | 5-10 per participant | Full transcripts with metrics |
| `questionnaire_responses` | 1 per participant | Perception scales, demographics |
| `honesty_codings` | 2 per participant (2 raters) | Feedback quality ratings |

### Key Timestamps
- `timestamp_session_start` - Consent page
- `timestamp_chat_start` - First chat message
- `timestamp_chat_end` - /chat/finish called
- `timestamp_questionnaire_start` - Questionnaire form loads
- `timestamp_questionnaire_submit` - Questionnaire submitted

### Export CSVs
1. **participants.csv** - One row per participant (engagement metrics, completion)
2. **transcripts.csv** - One row per message (full chat history with metrics)
3. **questionnaires.csv** - One row per participant (scales, demographics)
4. **honesty_codings.csv** - One row per coder per participant (feedback ratings)
5. **engagement_metrics.csv** - One row per participant (aggregated analysis variables)

### Analysis Pipeline (3 Stages)
1. **Descriptive Statistics** - Condition means/SDs for all DVs
2. **Regression Models** - Condition effect controlling for covariates
3. **Mediation Analysis** - Is psychological safety the mechanism?

---

## For Future Sessions

Everything you need is documented here:
- **Implementation**: See master-implementation-plan.md Phase 1-5
- **Data Model**: Check logging-specification.md for every variable
- **Deployment**: Follow Azure commands in master-implementation-plan.md
- **Testing**: Use checklist in temporal-booping-gadget.md

All files are version-controlled in `.claude/` directory in the project repo.

---

## Contact & Context

This is a master's thesis study on AI persona effects on psychological safety and feedback quality.
- **Participants**: 150-200 working students/interns/early-career professionals
- **Study Design**: 2-condition between-subjects (warm vs competent persona)
- **Duration**: 3-5 turn chat + post-interaction questionnaire
- **Analysis**: Multi-level regression with psychological safety as potential mediator
