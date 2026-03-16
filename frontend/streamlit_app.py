import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Feedback Assistant Study", page_icon="💬", layout="centered")


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
        "max_turns": 4,
        "turns_used": 0,
        "chat_history": [],
        "chat_completed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()
if st.session_state.stage == "consent":
    st.subheader("Study information")
    st.write(
        "You will read a short workplace scenario, interact with an AI feedback assistant, and then answer a questionnaire."
    )
    st.write(
        "Please participate only if you are at least 18 years old and have some experience with workplaces such as internships, working student roles, or early-career positions."
    )

    testing_mode = st.checkbox("Testing mode: choose condition manually")
    forced_condition = None

    if testing_mode:
        forced_condition = st.selectbox(
            "Condition for testing",
            ["warm", "competent"],
            index=0,
        )

    consent = st.checkbox("I have read the information and consent to participate.")

    if st.button("Start study", type="primary"):
        if not consent:
            st.error("You need to provide consent before continuing.")
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
            st.session_state.max_turns = data["max_turns"]
            st.session_state.chat_history = [
                {"role": "assistant", "content": data["opening_message"]}
            ]
            st.session_state.stage = "vignette"
            st.rerun()

elif st.session_state.stage == "vignette":
    st.subheader(st.session_state.vignette_title)
    st.caption(f"Testing only — condition: {st.session_state.condition}")
    st.info(st.session_state.vignette_text)
    if st.button("Continue to chat", type="primary"):
        st.session_state.stage = "chat"
        st.rerun()

elif st.session_state.stage == "chat":
    st.subheader("Chat")
    st.caption(
        f"Turns used: {st.session_state.turns_used} / {st.session_state.max_turns} | "
        f"Condition: {st.session_state.condition}"
    )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if not st.session_state.chat_completed:
        user_text = st.chat_input("Type your response here...")
        if user_text:
            st.session_state.chat_history.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.write(user_text)

            with st.spinner("Assistant is thinking..."):
                data = api_post(
                    "/chat",
                    {
                        "participant_id": st.session_state.participant_id,
                        "message": user_text,
                    },
                )
            st.session_state.turns_used = data["turns_used"]
            st.session_state.chat_completed = data["chat_completed"]
            st.session_state.chat_history.append(
                {"role": "assistant", "content": data["assistant_message"]["content"]}
            )
            st.rerun()
    else:
        st.success("You have completed the chat task.")
        if st.button("Continue to questionnaire", type="primary"):
            st.session_state.stage = "questionnaire"
            st.rerun()

elif st.session_state.stage == "questionnaire":
    st.subheader("Questionnaire")
    st.write("Please answer the following questions about your interaction.")

    with st.form("questionnaire_form"):
        st.markdown("**Perceived warmth / competence**")
        manip_warmth_friendly = st.slider("The assistant seemed friendly.", 1, 7, 4)
        manip_warmth_sincere = st.slider("The assistant seemed sincere.", 1, 7, 4)
        manip_competence_competent = st.slider("The assistant seemed competent.", 1, 7, 4)
        manip_competence_skilled = st.slider("The assistant seemed skilled.", 1, 7, 4)

        st.markdown("**Psychological safety in this interaction**")
        psych_safe_1 = st.slider("I felt safe to express any concerns I had.", 1, 7, 4)
        psych_safe_2 = st.slider("I could be honest without worrying about negative consequences.", 1, 7, 4)
        psych_safe_3 = st.slider("I felt comfortable sharing critical feedback.", 1, 7, 4)
        psych_safe_4 = st.slider("I did not feel judged by the assistant.", 1, 7, 4)
        psych_safe_5 = st.slider("This interaction made it easy to speak openly.", 1, 7, 4)

        st.markdown("**Background information**")
        ai_experience = st.slider("How experienced are you with conversational AI tools?", 1, 7, 3)
        organizational_tenure_years = st.number_input("How many years of organizational/work experience do you have?", min_value=0.0, step=0.5)
        age = st.number_input("Age", min_value=18, max_value=100, step=1)
        gender = st.text_input("Gender")
        industry = st.text_input("Industry")
        job_role = st.text_input("Job role")

        submitted = st.form_submit_button("Submit questionnaire")

        if submitted:
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
    st.subheader("Thank you")
    st.success("Your responses have been recorded.")
    st.write("You may now close this page.")
