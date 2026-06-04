# Fixed Retrieval Corpus Integration

## Overview

The chatbot uses a **fixed, curated retrieval corpus** to provide research-informed background knowledge during participant conversations. This corpus is **hidden from participants** and guides chatbot responses without exposing academic sources.

## Why Fixed Retrieval?

1. **Experimental Control**: All participants interact with identical evidence, preventing live-retrieval randomness from confounding the persona manipulation.
2. **Reproducibility**: Future researchers can audit and replicate the study with the same evidence base.
3. **Academic Rigor**: Evidence comes from peer-reviewed organizational psychology literature, not general web search.
4. **Thesis Defense**: A fixed corpus is easier to defend in methodology and results sections.

## Corpus Structure

The corpus is stored in `backend/app/data/retrieval_corpus.json` and contains:

- **25 evidence cards** organized into 8 empirical categories
- Each card includes:
  - `id`: stable identifier
  - `construct`: the workplace psychology construct (e.g., "psychological safety")
  - `complete_citation`: full academic reference with DOI
  - `source_type`: peer-reviewed journal, book chapter, foundational text, etc.
  - `category`: one of 8 categories (psychological safety, voice, feedback, communication, workload, fairness, conflict, confidentiality)
  - `tags`: searchable keywords
  - `evidence_summary`: paraphrased key finding (100-250 words, non-copyrighted)
  - `chatbot_behavior_guidance`: how the chatbot should use this evidence
  - `why_useful_for_participant_conversations`: why this evidence matters
  - `participant_visible`: always `false` (hidden background knowledge)
  - `verification`: metadata/content/relevance verification status

## Source Composition

- 21 peer-reviewed journal articles
- 1 peer-reviewed book chapter (annual series)
- 1 practitioner/foundational communication text (Stone, Patton, Heen)
- 1 foundational book chapter (Clark & Brennan)
- 1 edited academic book (Dutton & Ragins)

## How Retrieval Works

### 1. User Message → Retrieval

When a participant sends a message, the chatbot:

1. Sends the message to `RetrievalService.retrieve()`
2. Attempts **semantic similarity retrieval** using OpenAI embeddings (if enabled)
3. Falls back to **keyword + tag matching** if embeddings fail or are disabled
4. Returns top K cards (default K=3) with similarity scores

### 2. Retrieval Methods

#### Embedding-Based (Default)
- Uses OpenAI's `text-embedding-3-small` model
- Computes cosine similarity between query embedding and cached card embeddings
- **Advantages**: Better semantic understanding, tolerates paraphrasing
- **Cost**: ~$0.02 per 1M tokens for embeddings

#### Keyword Fallback
- Matches query words against card titles, text, and tags
- Combines 70% keyword score + 30% tag overlap score
- **Advantages**: Fast, no API calls, works offline
- **Fallback**: Activates if embeddings fail or are disabled

### 3. Retrieved Context Injection

Retrieved cards are injected into the system prompt as **hidden guidance**:

```
Relevant research-informed guidance from the fixed retrieval corpus:

[Evidence 1]
Construct: Psychological safety and interpersonal risk-taking
Summary: Psychological safety is the team-level belief that interpersonal 
risk-taking—asking questions, admitting mistakes, voicing concerns—is safe...
Guidance: When participant shares concerns or hesitation about speaking up...

[Evidence 2]
...
```

The system prompt explicitly instructs the chatbot:
- Use this guidance as **background only**
- Do not mention the corpus
- Do not cite papers or sources
- Do not make the conversation feel academic
- Respond naturally and maintain the assigned persona

### 4. Retrieval Logging

Every retrieval is logged to track:
- `session_id`: participant ID
- `turn_index`: conversation turn
- `user_message_text`: what the participant said
- `retrieved_card_ids`: which cards were retrieved
- `retrieved_card_constructs`: constructs/titles of cards
- `retrieval_scores`: similarity/relevance scores
- `retrieval_method`: "embedding", "keyword_fallback", or "disabled"
- `timestamp_created`: when retrieval happened

Logs enable:
- Post-hoc analysis of whether retrieval helped
- Validation that all 25 cards were used
- Evidence that persona, not corpus, drove differences

## Configuration

### Environment Variables

```bash
# Enable/disable retrieval entirely
RETRIEVAL_ENABLED=true

# Use OpenAI embeddings (false = keyword fallback only)
RETRIEVAL_USE_EMBEDDINGS=true

# Enable logging of retrieval metadata
RETRIEVAL_LOGGING_ENABLED=true

# Number of cards to retrieve per message
TOP_K_RETRIEVAL=3

# Debug mode (enables /debug endpoints)
DEBUG=false
```

### Defaults

```python
retrieval_enabled: bool = True
retrieval_use_embeddings: bool = True
retrieval_logging_enabled: bool = True
top_k_retrieval: int = 3
debug: bool = False
```

## API Endpoints

### Chat (Main)
- `POST /chat` - Send message, get response with embedded retrieval context
  - Returns: assistant message with hidden retrieval guidance applied

### Export
- `GET /export/retrieval_logs.csv` - Download retrieval metadata for all participants
  - Columns: participant_id, turn_index, user_message, retrieved_card_ids, scores, method, timestamp

### Debug (DEBUG=true only)
- `GET /debug/retrieval?q=query` - Test retrieval with a sample query
  - Returns: retrieved card IDs, constructs, categories, tags, scores
- `POST /debug/retrieval` - POST-based retrieval test
  - Example: `{"query": "I do not feel safe giving feedback"}`

## Testing Retrieval Locally

### 1. Enable Debug Mode

```bash
DEBUG=true
```

### 2. Test Sample Queries

```bash
curl "http://localhost:8000/debug/retrieval?q=I%20do%20not%20feel%20safe%20giving%20honest%20feedback%20to%20my%20manager"
```

Expected response:
```json
{
  "query": "I do not feel safe giving honest feedback...",
  "retrieved_count": 3,
  "retrieval_method": "embedding",
  "cards": [
    {
      "id": "psych_safety_001",
      "construct": "Psychological safety and interpersonal risk-taking",
      "category": "1_psychological_safety_and_speaking_up",
      "tags": ["psychological_safety", "voice", "team_dynamics", ...],
      "score": 0.8432,
      "evidence_summary": "Psychological safety is the team-level belief..."
    },
    ...
  ]
}
```

### 3. Test Queries

Verify retrieval with these queries:

#### Safety Query
```
I do not feel safe giving honest feedback to my manager.
```
Expected: psych_safety_*, org_silence_* cards

#### Workload Query
```
My workload is too much and priorities keep changing.
```
Expected: role_ambiguity_*, conflict_* cards

#### Recognition Query
```
I feel like my work is not recognized.
```
Expected: fairness_recognition_* cards

#### Conflict Query
```
I had a conflict with a colleague and now I avoid speaking up.
```
Expected: conflict_*, org_silence_* cards

#### Confidentiality Query
```
I am not sure whether my feedback will stay confidential.
```
Expected: confidentiality_trust_*, org_silence_* cards

## Corpus Validation

The retrieval service validates the corpus on startup:

```python
# Validation checks:
1. Corpus file exists at backend/app/data/retrieval_corpus.json
2. corpus_metadata exists
3. evidence_items exists and has exactly 25 items
4. Every item has required fields
5. All participant_visible values are false
6. All verification statuses are complete
```

If validation fails:
- **Development**: Logs error and raises exception
- **Production**: Logs error, sets CORPUS_LOADED=False, retrieval disabled gracefully

## Export & Analysis

### Retrieval Logs CSV

```csv
participant_id,condition,turn_index,user_message_text,retrieved_card_ids,retrieved_card_constructs,retrieval_scores,retrieval_method,retrieval_enabled,timestamp_created
p_001,warm,1,"My manager never listens to me...","psych_safety_002,org_silence_001,manager_communication_002","Safety in asymmetric power relationships; Organizational silence...","0.8432,0.7891,0.7234",embedding,true,2026-06-04T12:34:56
...
```

### Analysis Questions

1. **Retrieval coverage**: Which cards were retrieved most frequently?
2. **Retrieval method**: Did embeddings or keyword fallback work better?
3. **Relevance**: Did retrieved cards match participant concerns?
4. **Persona independence**: Did both conditions retrieve similar cards?

## Limitations & Risks

### Limitations

1. **25 cards only**: Limited semantic coverage. Edge-case topics may retrieve generic cards.
2. **Keyword fallback**: Without embeddings, retrieval is less nuanced.
3. **No real-time adaptation**: Corpus is fixed; cannot add new evidence mid-study.
4. **Single language**: Corpus is English-only.

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Retrieval enriches one condition more than the other | Analysis: Export retrieval logs and verify both conditions retrieve similar cards. If not, note in limitations. |
| Embeddings API fails mid-study | Fallback: Keyword retrieval is automatic and works offline. |
| Corpus file deleted/corrupted | CI/CD: Validate corpus file on deployment. Commit to git with version control. |
| Card text copied from sources | Content check: All summaries paraphrased, no passages >few sentences, cited. |

## Future Improvements

1. **Hybrid scoring**: Weight tag matches + keyword overlap + embeddings
2. **Query expansion**: Expand queries with synonyms before retrieval
3. **LLM-based re-ranking**: Use LLM to re-rank retrieved cards by relevance
4. **Per-condition corpus**: Different corpus for warm vs. competent personas (if theory changes)
5. **Dynamic corpus loading**: Load corpus from database instead of JSON for runtime updates

## References

### Implementation Files

- `backend/app/data/retrieval_corpus.py` - Corpus loader with validation
- `backend/app/services/retrieval.py` - RetrievalService with embedding + fallback
- `backend/app/services/chat_service.py` - Chat integration with retrieval context
- `backend/app/models.py` - RetrievalLog database model
- `backend/app/routers/export.py` - Retrieval logs export endpoint
- `backend/app/routers/debug.py` - Debug retrieval endpoints

### Configuration

- `backend/app/config.py` - Settings for retrieval control

### Environment Variables

```
RETRIEVAL_ENABLED=true
RETRIEVAL_USE_EMBEDDINGS=true
RETRIEVAL_LOGGING_ENABLED=true
TOP_K_RETRIEVAL=3
DEBUG=false
```
