import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Feedback Assistant Study",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def api_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def init_state() -> None:
    defaults = {
        "stage": "consent",
        "participant_id": None,
        "condition": None,
        "vignette_title": None,
        "vignette_text": None,
        "opening_message": None,
        "turns_used": 0,
        "chat_history": [],
        "chat_completed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

# Add loading state to defaults
if "loading" not in st.session_state:
    st.session_state.loading = False

if st.session_state.stage == "consent":
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.title("AI Feedback Assistant Study")
        st.markdown("### Welcome")
        st.markdown(
            "You will read a short workplace scenario, interact with an AI feedback assistant, "
            "and then answer a questionnaire about your experience."
        )

        st.markdown("### Who can participate")
        st.info(
            "✓ You must be at least 18 years old\n"
            "✓ You should have some workplace experience (internships, part-time roles, early-career positions)"
        )

        st.markdown("### What to expect")
        st.markdown(
            "1. **Scenario** (1 min) — Read a workplace situation\n"
            "2. **Chat** (5 min) — Have a 3-5 turn conversation with an AI assistant\n"
            "3. **Questionnaire** (3 min) — Share your thoughts and background"
        )

    with col2:
        with st.container(border=True):
            st.markdown("### Participate")

            consent = st.checkbox("I have read and agree to participate in this study")

            testing_mode = st.checkbox("🧪 Testing mode", help="Choose condition manually for testing")
            forced_condition = None

            if testing_mode:
                forced_condition = st.radio(
                    "Select condition",
                    ["warm", "competent"],
                    horizontal=False,
                )

            st.divider()

            if st.button("Begin Study →", type="primary", use_container_width=True):
                if not consent:
                    st.error("Please agree to participate to continue.")
                else:
                    payload = {"consented": True}
                    if testing_mode and forced_condition:
                        payload["forced_condition"] = forced_condition

                    data = api_post("/session/start", payload)
                    st.session_state.participant_id = data["participant_id"]
                    st.session_state.condition = data["condition"]
                    st.session_state.vignette_title = data["vignette_title"]
                    st.session_state.vignette_text = data["vignette_text"]
                    st.session_state.opening_message = data["opening_message"]
                    st.session_state.min_turns = data.get("min_turns", 3)
                    st.session_state.max_turns = data.get("max_turns", 5)
                    st.session_state.chat_history = [
                        {"role": "assistant", "content": data["opening_message"]}
                    ]
                    st.session_state.stage = "vignette"
                    st.rerun()

elif st.session_state.stage == "vignette":
    st.title(st.session_state.vignette_title)
    st.caption(f"Step 1 of 3 • Testing mode: {st.session_state.condition}")

    st.divider()

    st.info(st.session_state.vignette_text)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Begin Chat →", type="primary", use_container_width=True):
            st.session_state.stage = "chat"
            st.rerun()

elif st.session_state.stage == "chat":
    # Top header with condition info
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.subheader("Chat with AI Assistant")
    with col_header2:
        st.caption(f"Mode: {st.session_state.condition}")

    st.divider()

    # Main chat layout
    chat_col, side_col = st.columns([3, 1], gap="medium")

    with chat_col:
        # Chat history display in scrollable container
        chat_container = st.container(height=600, border=True)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Show loading indicator in the container if waiting for response
            if st.session_state.loading:
                with st.chat_message("assistant"):
                    st.write("✨ Thinking...")

        # Chat input below container
        if not st.session_state.chat_completed:
            user_text = st.chat_input("Type your response here...")

            # First interaction: capture the message
            if user_text and not st.session_state.loading:
                st.session_state.chat_history.append({"role": "user", "content": user_text})
                st.session_state.loading = True
                st.rerun()

        # Handle API call on next render if loading
        if st.session_state.loading and not st.session_state.chat_completed:
            if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["role"] == "user":
                try:
                    data = api_post(
                        "/chat",
                        {
                            "participant_id": st.session_state.participant_id,
                            "message": st.session_state.chat_history[-1]["content"],
                        },
                    )
                    st.session_state.turns_used = data["turns_used"]
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": data["assistant_message"]["content"]}
                    )
                except Exception as e:
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": f"Error: {str(e)}"}
                    )
                finally:
                    st.session_state.loading = False
                    st.rerun()

    # Side panel with controls and info
    with side_col:
        st.markdown("### Session Info")

        # Turn counter
        st.metric(label="Turns completed", value=st.session_state.turns_used)

        # Progress indicator
        st.info(f"Min: 3 turns • Max: 5 turns")

        # Finish button
        st.divider()
        if not st.session_state.chat_completed:
            if st.button("✓ Finish Chat", type="primary", use_container_width=True, key="finish_btn"):
                try:
                    api_post(
                        "/chat/finish",
                        {"participant_id": st.session_state.participant_id},
                    )
                    st.session_state.chat_completed = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Cannot finish yet: {str(e)}")
        else:
            st.success("✓ Chat completed!")
            if st.button("Continue to Questionnaire →", type="primary", use_container_width=True, key="questionnaire_btn"):
                st.session_state.stage = "questionnaire"
                st.rerun()

elif st.session_state.stage == "questionnaire":
    st.title("Feedback Questionnaire")
    st.caption("Step 3 of 3 • Almost done! Please answer the following questions.")
    st.divider()

    with st.form("questionnaire_form"):
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.subheader("📊 How did you perceive the assistant?")
            manip_warmth_friendly = st.slider(
                "The assistant seemed friendly.",
                1, 7, 4,
                help="1 = Not friendly, 7 = Very friendly"
            )
            manip_warmth_sincere = st.slider(
                "The assistant seemed sincere.",
                1, 7, 4,
                help="1 = Not sincere, 7 = Very sincere"
            )
            manip_competence_competent = st.slider(
                "The assistant seemed competent.",
                1, 7, 4,
                help="1 = Not competent, 7 = Very competent"
            )
            manip_competence_skilled = st.slider(
                "The assistant seemed skilled.",
                1, 7, 4,
                help="1 = Not skilled, 7 = Very skilled"
            )

        with col2:
            st.subheader("🛡️ How safe did you feel?")
            psych_safe_1 = st.slider(
                "I felt safe to express any concerns I had.",
                1, 7, 4
            )
            psych_safe_2 = st.slider(
                "I could be honest without worrying about negative consequences.",
                1, 7, 4
            )
            psych_safe_3 = st.slider(
                "I felt comfortable sharing critical feedback.",
                1, 7, 4
            )
            psych_safe_4 = st.slider(
                "I felt able to say what I really thought.",
                1, 7, 4
            )
            psych_safe_5 = st.slider(
                "I did not feel judged when expressing concerns.",
                1, 7, 4
            )

        st.divider()

        st.subheader("ℹ️ About you")
        col_bg1, col_bg2, col_bg3 = st.columns([1, 1, 1])

        with col_bg1:
            ai_experience = st.slider(
                "Experience with conversational AI",
                1, 7, 3,
                help="1 = No experience, 7 = Very experienced"
            )
            organizational_tenure_years = st.number_input(
                "Years of work experience",
                min_value=0.0,
                max_value=70.0,
                step=0.5
            )

        with col_bg2:
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=100,
                step=1
            )
            gender = st.text_input("Gender (optional)")

        with col_bg3:
            industry = st.text_input("Industry (optional)")
            job_role = st.text_input("Job role (optional)")

        st.divider()

        submitted = st.form_submit_button("✓ Submit & Complete", type="primary", use_container_width=True)

        if submitted:
            with st.spinner("Submitting your responses..."):
                data = api_post(
                    "/questionnaire",
                    {
                        "participant_id": st.session_state.participant_id,
                        "manip_warmth_friendly": manip_warmth_friendly,
                        "manip_warmth_sincere": manip_warmth_sincere,
                        "manip_competence_competent": manip_competence_competent,
                        "manip_competence_skilled": manip_competence_skilled,
                        "psych_safe_1": psych_safe_1,
                        "psych_safe_2": psych_safe_2,
                        "psych_safe_3": psych_safe_3,
                        "psych_safe_4": psych_safe_4,
                        "psych_safe_5": psych_safe_5,
                        "ai_experience": ai_experience,
                        "organizational_tenure_years": organizational_tenure_years,
                        "age": age,
                        "gender": gender,
                        "industry": industry,
                        "job_role": job_role,
                    },
                )
                st.session_state.stage = "done"
                st.session_state.psychological_safety_mean = data["psychological_safety_mean"]
                st.rerun()

elif st.session_state.stage == "done":
    st.title("✓ Study Complete")
    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.success("Your responses have been recorded successfully!")

    st.markdown("""
    ### Thank you for participating!
    Your feedback and responses will help us understand human-AI interaction better.

    Your **psychological safety score**: **{:.2f}** (out of 7)
    """.format(st.session_state.psychological_safety_mean))

    st.info("You may now close this page.")
    st.divider()
    st.caption("Study ID: " + st.session_state.participant_id[:8] + "...")
