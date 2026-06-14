"""Semantic relevance classifier using LLM to judge workplace scenario fit."""

import json
import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

WORKPLACE_SCENARIO = """
Workplace Scenario:
A junior team member or intern has noticed issues:
- Tasks are assigned at the last minute
- Priorities change without explanation
- Responsibilities aren't always clear
- Important information comes too late
- Different people give conflicting instructions
- Work sometimes gets duplicated

The person is newer to the team and unsure how to bring these up directly.
"""

CLASSIFICATION_PROMPT_TEMPLATE = """You are judging whether a user message is relevant to a workplace feedback scenario.

{scenario}

Current study question: {current_question}

User message: "{user_message}"

Classify this message into ONE of these categories:

1. substantive_on_topic:
   - Clear workplace concern, example, opinion, suggestion, or answer
   - Directly addresses team/work issues or provides concrete feedback
   - Examples: "People complain privately but say nothing in meetings", "My manager gives vague instructions"

2. vague_but_relevant:
   - Vague or emotional answer that COULD plausibly relate to the workplace scenario
   - Lacks specifics but seems to address team/work/feedback themes
   - Examples: "I feel neglected", "They don't care", "No one listens", "I'm tired of it"
   - IMPORTANT: If uncertain between this and off-topic, choose this

3. clearly_off_topic:
   - Clearly unrelated to workplace feedback or the scenario
   - Personal interests, random topics, jokes, greetings with no content
   - Examples: "i like food", "banana", "tell me a joke", "what is the weather", "hello"

4. safety_concern:
   - Self-harm, suicide, or harm to others
   - Serious crisis content requiring immediate support
   - Examples: "I want to hurt myself", "I don't want to live"

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "label": "substantive_on_topic|vague_but_relevant|clearly_off_topic|safety_concern",
  "confidence": 0.0-1.0,
  "should_advance_study_flow": true or false,
  "is_valid_turn": true or false,
  "brief_reason": "one sentence explaining the classification"
}}

Rules:
- Confidence: 0.5-1.0, where 1.0 is certain
- should_advance_study_flow: true only for substantive_on_topic (proceed to next question)
- is_valid_turn: true for substantive_on_topic and vague_but_relevant (count toward turn limit)
- If uncertain, lean toward vague_but_relevant
- Short brief_reason (one sentence max)
"""


class SemanticRelevanceClassifier:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def classify(
        self, user_message: str, current_follow_up_key: str = None
    ) -> dict:
        """
        Classify a user message for semantic relevance to workplace scenario.

        Returns:
            {
                "label": str,
                "confidence": float,
                "should_advance_study_flow": bool,
                "is_valid_turn": bool,
                "brief_reason": str
            }
        """
        # Map follow-up keys to human-readable questions
        question_map = {
            "issue_detail": "What's the main issue you're seeing?",
            "impact": "How does this affect your work or the team?",
            "causes": "What do you think is the root cause?",
            "improvement": "What would fix it?",
            "reflection": "Is there anything else important you'd like to add?",
        }

        current_question = question_map.get(
            current_follow_up_key, "Please describe your feedback about the team situation"
        )

        prompt = CLASSIFICATION_PROMPT_TEMPLATE.format(
            scenario=WORKPLACE_SCENARIO,
            current_question=current_question,
            user_message=user_message,
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a classifier. Respond ONLY with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temp for consistent classification
            )

            response_text = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            classification = json.loads(response_text)

            # Validate required fields
            required_fields = [
                "label",
                "confidence",
                "should_advance_study_flow",
                "is_valid_turn",
                "brief_reason",
            ]
            for field in required_fields:
                if field not in classification:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure label is valid
            valid_labels = [
                "substantive_on_topic",
                "vague_but_relevant",
                "clearly_off_topic",
                "safety_concern",
            ]
            if classification["label"] not in valid_labels:
                raise ValueError(f"Invalid label: {classification['label']}")

            return classification

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Classification error: {e}")
            # Fallback: treat as vague_but_relevant to err on the side of caution
            return {
                "label": "vague_but_relevant",
                "confidence": 0.5,
                "should_advance_study_flow": False,
                "is_valid_turn": True,
                "brief_reason": "Classifier error; treating as potentially relevant",
            }
        except Exception as e:
            logger.error(f"Unexpected classification error: {e}")
            return {
                "label": "vague_but_relevant",
                "confidence": 0.5,
                "should_advance_study_flow": False,
                "is_valid_turn": True,
                "brief_reason": "Unexpected error; treating as potentially relevant",
            }
