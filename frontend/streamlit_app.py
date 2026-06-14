import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Feedback Study",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern color palette
COLORS = {
    "bg": "#F7F8FB",
    "card": "#FFFFFF",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "primary": "#3B82F6",
    "teal": "#14B8A6",
    "assistant_bubble": "#EEF4FF",
    "user_bubble": "#2563EB",
}

# Custom CSS for modern design
st.markdown(f"""
<style>
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }}

    body {{
        background-color: {COLORS['bg']};
        color: {COLORS['text']};
    }}

    .main {{
        background-color: {COLORS['bg']};
        padding: 1.5rem;
    }}

    .stForm {{
        background-color: transparent;
        border: none;
    }}

    /* Card styling */
    .card {{
        background-color: {COLORS['card']};
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid {COLORS['border']};
        margin-bottom: 1.5rem;
    }}

    /* Button styling */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        background-color: #2563EB;
        box-shadow: 0 4px 12px rgba(59,130,246,0.15);
    }}

    .stButton > button:disabled {{
        background-color: {COLORS['muted']};
        opacity: 0.6;
    }}

    /* Title styling */
    h1 {{
        color: {COLORS['text']};
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}

    h2 {{
        color: {COLORS['text']};
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }}

    h3 {{
        color: {COLORS['text']};
        font-weight: 600;
    }}

    /* Slider styling */
    .stSlider {{
        padding: 1rem 0;
    }}

    /* Warning styling */
    .stWarning {{
        background-color: #FEF3C7;
        border-radius: 8px;
        border-left: 4px solid #F59E0B;
    }}

    /* Info styling */
    .stInfo {{
        background-color: {COLORS['assistant_bubble']};
        border-radius: 8px;
        border-left: 4px solid {COLORS['primary']};
    }}

    /* Caption styling */
    .stCaption {{
        color: {COLORS['muted']};
        font-size: 0.875rem;
    }}

    /* Checkbox styling */
    .stCheckbox {{
        margin-bottom: 1rem;
    }}

    /* Radio styling */
    .stRadio {{
        padding: 0.5rem 0;
    }}

    /* Divider */
    hr {{
        border: none;
        border-top: 1px solid {COLORS['border']};
        margin: 2rem 0;
    }}

    /* Metric styling */
    .stMetric {{
        background-color: {COLORS['card']};
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}

    /* Chat container styling */
    .chat-container {{
        display: flex !important;
        flex-direction: column;
        gap: 0.75rem;
        padding: 1.5rem;
        background-color: {COLORS['card']};
        border-radius: 12px;
        min-height: 400px;
        border: 1px solid {COLORS['border']};
        margin-bottom: 1rem;
    }}

    /* Message row styling */
    .message-row {{
        display: flex !important;
        align-items: flex-end;
        gap: 0.5rem;
        margin-bottom: 0;
        width: 100%;
    }}

    .message-row.user {{
        justify-content: flex-end;
    }}

    /* Avatar styling */
    .avatar {{
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 28px;
        width: 28px;
        height: 28px;
        border-radius: 4px;
        font-size: 1rem;
        flex-shrink: 0;
        margin-top: 0.25rem;
    }}

    .avatar.assistant {{
        background-color: {COLORS['assistant_bubble']};
    }}

    .avatar.user {{
        background-color: transparent;
        color: {COLORS['text']};
    }}

    /* Chat bubble styling */
    .chat-bubble {{
        padding: 0.75rem 1rem;
        border-radius: 12px;
        line-height: 1.5;
        word-wrap: break-word;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        max-width: 75%;
        flex-wrap: wrap;
    }}

    .chat-bubble.assistant {{
        background-color: {COLORS['assistant_bubble']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
    }}

    .chat-bubble.user {{
        background-color: {COLORS['user_bubble']};
        color: white;
    }}

    /* Input area styling */
    .input-container {{
        display: flex;
        gap: 0.75rem;
        padding: 1rem;
        background-color: {COLORS['card']};
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
    }}

    .input-container input {{
        flex: 1;
        padding: 0.75rem;
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        font-size: 1rem;
    }}

    /* Loading indicator */
    .loading-indicator {{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.5rem;
        color: {COLORS['muted']};
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }}

    /* Turn counter */
    .turn-counter {{
        text-align: center;
        color: {COLORS['muted']};
        font-size: 0.875rem;
        margin: 1rem 0 0 0;
    }}

    /* Chat header */
    .chat-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }}

    .chat-header h1 {{
        margin: 0;
        font-size: 1.75rem;
    }}
</style>
""", unsafe_allow_html=True)


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


def progress_indicator(current: int, total: int = 3):
    """Display modern progress indicator"""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem;">
        <span style="font-size: 0.875rem; color: {COLORS['muted']};">
            Step {current} of {total}
        </span>
        <div style="flex-grow: 1; height: 4px; background-color: {COLORS['border']}; border-radius: 2px; overflow: hidden;">
            <div style="width: {(current/total)*100}%; height: 100%; background-color: {COLORS['primary']}; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_chat_messages():
    """Render all chat messages in a styled container"""
    messages_html = '<div class="chat-container">'

    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            avatar_icon = "🤖"
            messages_html += f"""<div class="message-row">
    <div class="avatar assistant">{avatar_icon}</div>
    <div class="chat-bubble assistant">{msg["content"]}</div>
</div>"""
        else:
            avatar_icon = "👤"
            messages_html += f"""<div class="message-row user">
    <div class="chat-bubble user">{msg["content"]}</div>
    <div class="avatar user">{avatar_icon}</div>
</div>"""

    if st.session_state.loading:
        messages_html += '<div class="loading-indicator">✨ Assistant is thinking...</div>'

    messages_html += '</div>'
    return messages_html


init_state()

if "loading" not in st.session_state:
    st.session_state.loading = False

# CONSENT PAGE
if st.session_state.stage == "consent":
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("# 👋 Welcome")
        st.markdown("""
        You will read a short workplace scenario, interact with an AI assistant, and answer a brief questionnaire about your experience.

        **What to expect:**
        - **Scenario** (1 min) — Read a workplace situation
        - **Chat** (5 min) — Have a 3-5 turn conversation with an AI assistant
        - **Questionnaire** (3 min) — Share your thoughts and background
        """)

        st.markdown("### Eligibility")
        st.markdown("✓ You must be at least 18 years old  \n✓ You should have some workplace experience")

    with col2:
        with st.container():
            st.markdown(f"""
            <div class="card">
                <h3 style="margin-top: 0;">Ready to participate?</h3>
            </div>
            """, unsafe_allow_html=True)

            consent = st.checkbox("I have read and agree to participate in this study")

            testing_mode = st.checkbox("🧪 Testing mode (developers only)")
            forced_condition = None

            if testing_mode:
                forced_condition = st.radio(
                    "Select condition",
                    ["warm", "competent"],
                    horizontal=True,
                )

            if st.button("Begin Study →", use_container_width=True):
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

# VIGNETTE PAGE
elif st.session_state.stage == "vignette":
    progress_indicator(1)

    st.markdown("# 📋 Scenario")

    st.markdown(f"""
    <div class="card">
        {st.session_state.vignette_text}
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Begin Chat →", use_container_width=True):
            st.session_state.stage = "chat"
            st.rerun()

# CHAT PAGE
elif st.session_state.stage == "chat":
    progress_indicator(2)

    st.markdown("# 💬 Chat")

    # Chat display with messages
    st.markdown(render_chat_messages(), unsafe_allow_html=True)

    # Turn counter
    st.markdown(f'<div class="turn-counter">Turn {st.session_state.turns_used} of {st.session_state.max_turns}</div>', unsafe_allow_html=True)

    # Chat input and controls
    if not st.session_state.chat_completed:
        user_text = st.chat_input("Type your response here...", key="chat_input")

        if user_text and not st.session_state.loading:
            st.session_state.chat_history.append({"role": "user", "content": user_text})
            st.session_state.loading = True
            st.rerun()

        # Handle API call
        if st.session_state.loading:
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
                    st.session_state.chat_completed = data["chat_completed"]
                except Exception as e:
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": f"Error: {str(e)}"}
                    )
                finally:
                    st.session_state.loading = False
                    st.rerun()

        # Show Finish Chat button only after min turns are completed
        if st.session_state.turns_used >= st.session_state.min_turns:
            st.markdown(f'<div style="text-align: center; margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
            col_center = st.columns([1, 1, 1])[1]
            with col_center:
                if st.button("✓ Finish Chat", use_container_width=True):
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
        col_center = st.columns([1, 1, 1])[1]
        with col_center:
            if st.button("Continue to Questionnaire →", use_container_width=True):
                st.session_state.stage = "questionnaire"
                st.rerun()

# QUESTIONNAIRE PAGE
elif st.session_state.stage == "questionnaire":
    progress_indicator(3)

    st.markdown("# 📝 Feedback Questionnaire")
    st.markdown("Please answer all required questions.")

    with st.form("questionnaire_form"):
        def likert_question(label: str, key: str, anchor_low: str = "Strongly disagree", anchor_mid: str = "Neither", anchor_high: str = "Strongly agree"):
            st.markdown(f"**{label}**")
            st.caption(f"1 = {anchor_low} | 4 = {anchor_mid} | 7 = {anchor_high}")
            value = st.radio(
                label=label,
                options=[1, 2, 3, 4, 5, 6, 7],
                format_func=lambda x: str(x),
                horizontal=True,
                key=key,
                label_visibility="collapsed"
            )
            return value

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown(f"""
            <div class="card">
                <h3>📊 How did you perceive the assistant?</h3>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Warmth**")
            perc_warm_warm = likert_question("The assistant seemed warm.", "perc_warm_warm")
            perc_warm_friendly = likert_question("The assistant seemed friendly.", "perc_warm_friendly")
            perc_warm_understanding = likert_question("The assistant seemed understanding.", "perc_warm_understanding")

            st.markdown("**Competence**")
            perc_comp_competent = likert_question("The assistant seemed competent.", "perc_comp_competent")
            perc_comp_structured = likert_question("The assistant seemed structured.", "perc_comp_structured")
            perc_comp_capable = likert_question("The assistant seemed capable.", "perc_comp_capable")

        with col2:
            st.markdown(f"""
            <div class="card">
                <h3>🛡️ How safe did you feel during the conversation?</h3>
            </div>
            """, unsafe_allow_html=True)

            psych_safe_1 = likert_question("I felt safe to express any concerns I had.", "psych_safe_1")
            psych_safe_2 = likert_question("I could be honest without worrying about negative consequences.", "psych_safe_2")
            psych_safe_3 = likert_question("I felt comfortable sharing critical feedback.", "psych_safe_3")
            psych_safe_4 = likert_question("I felt able to say what I really thought.", "psych_safe_4")
            psych_safe_5 = likert_question("I did not feel judged when expressing concerns.", "psych_safe_5")

        st.divider()

        st.markdown(f"""
        <div class="card">
            <h3>💭 How openly did you respond?</h3>
        </div>
        """, unsafe_allow_html=True)

        openness_1 = likert_question("I answered the assistant honestly.", "openness_1")
        openness_2 = likert_question("I shared my real thoughts during the conversation.", "openness_2")
        openness_3 = likert_question("I gave concrete details about the situation.", "openness_3")
        openness_4 = likert_question("I held back some things I was thinking.", "openness_4")
        st.caption("(Note: This item will be reverse-scored in analysis)")

        st.divider()

        st.markdown(f"""
        <div class="card">
            <h3>ℹ️ About you</h3>
        </div>
        """, unsafe_allow_html=True)

        col_bg1, col_bg2, col_bg3 = st.columns([1, 1, 1])

        with col_bg1:
            st.markdown("**Experience with conversational AI**")
            st.caption("1 = No experience | 7 = Very experienced")
            ai_experience = st.radio(
                label="Experience",
                options=[1, 2, 3, 4, 5, 6, 7],
                format_func=lambda x: str(x),
                horizontal=True,
                key="ai_experience",
                label_visibility="collapsed"
            )
            form_responses["ai_experience"] = ai_experience

            years_work_experience = st.number_input(
                "Years of work experience",
                min_value=0.0,
                max_value=70.0,
                step=0.5,
                value=None
            )

        with col_bg2:
            age = st.number_input(
                "Age (optional)",
                min_value=18,
                max_value=100,
                step=1,
                value=None
            )
            gender = st.selectbox(
                "Gender (optional)",
                ["", "Female", "Male", "Prefer not to say"],
                index=0
            )

        with col_bg3:
            industry = st.text_input("Industry (optional)")
            job_role = st.text_input("Job role (optional)")

        st.divider()

        submitted = st.form_submit_button(
            "✓ Submit & Complete",
            use_container_width=True
        )

        if submitted:
            # Validate all required fields are answered
            required_items = [
                "perc_warm_warm", "perc_warm_friendly", "perc_warm_understanding",
                "perc_comp_competent", "perc_comp_structured", "perc_comp_capable",
                "psych_safe_1", "psych_safe_2", "psych_safe_3", "psych_safe_4", "psych_safe_5",
                "openness_1", "openness_2", "openness_3", "openness_4",
                "ai_experience"
            ]

            missing_items = [key for key in required_items if st.session_state.get(key) is None]

            if missing_items:
                st.error(f"⚠️ Please answer all required questions before submitting. Missing {len(missing_items)} answer(s).")
                st.stop()

            # All required items answered, proceed with submission
            with st.spinner("Submitting your responses..."):
                data = api_post(
                    "/questionnaire",
                    {
                        "participant_id": st.session_state.participant_id,
                        "perc_warm_warm": st.session_state.perc_warm_warm,
                        "perc_warm_friendly": st.session_state.perc_warm_friendly,
                        "perc_warm_understanding": st.session_state.perc_warm_understanding,
                        "perc_comp_competent": st.session_state.perc_comp_competent,
                        "perc_comp_structured": st.session_state.perc_comp_structured,
                        "perc_comp_capable": st.session_state.perc_comp_capable,
                        "psych_safe_1": st.session_state.psych_safe_1,
                        "psych_safe_2": st.session_state.psych_safe_2,
                        "psych_safe_3": st.session_state.psych_safe_3,
                        "psych_safe_4": st.session_state.psych_safe_4,
                        "psych_safe_5": st.session_state.psych_safe_5,
                        "openness_1": st.session_state.openness_1,
                        "openness_2": st.session_state.openness_2,
                        "openness_3": st.session_state.openness_3,
                        "openness_4": st.session_state.openness_4,
                        "ai_experience": st.session_state.ai_experience,
                        "years_work_experience": years_work_experience,
                        "age": age if age else None,
                        "gender": gender if gender else None,
                        "industry": industry if industry else None,
                        "job_role": job_role if job_role else None,
                    },
                )
                st.session_state.stage = "done"
                st.session_state.psychological_safety_mean = data["psychological_safety_mean"]
                st.rerun()

# COMPLETION PAGE
elif st.session_state.stage == "done":
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div class="card" style="max-width: 600px; margin: 0 auto;">
            <h1 style="font-size: 3rem; margin: 0;">✓</h1>
            <h2>Thank you for participating</h2>
            <p style="color: {COLORS['muted']}; font-size: 1.1rem; margin: 1rem 0;">
                Your responses have been submitted successfully.
            </p>
            <p style="color: {COLORS['muted']};">
                You may now close this page.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
