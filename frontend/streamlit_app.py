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

# Mobile viewport settings
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
""", unsafe_allow_html=True)

# Color palette - will adapt to system dark/light mode preference
COLORS_LIGHT = {
    "bg": "#FFFFFF",
    "card": "#F8F6FF",
    "text": "#111827",
    "muted": "#4B5563",
    "border": "#D4CAFF",
    "primary": "#7C3AED",
    "teal": "#7C3AED",
    "assistant_bubble": "#EDE9FE",
    "user_bubble": "#7C3AED",
}

COLORS_DARK = {
    "bg": "#0F1117",
    "card": "#1F2937",
    "card_secondary": "#27233A",
    "text": "#F9FAFB",
    "muted": "#D1D5DB",
    "border": "#4C3F73",
    "primary": "#8B5CF6",
    "teal": "#8B5CF6",
    "accent": "#C4B5FD",
    "assistant_bubble": "#252A3A",
    "user_bubble": "#8B5CF6",
    "input_bg": "#2A2D36",
}

# Use light mode colors as default
COLORS = COLORS_LIGHT

# Custom CSS with dark mode support
st.markdown(f"""
<style>
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }}

    /* Light Mode (Default) */
    body {{
        background-color: {COLORS_LIGHT['bg']};
        color: {COLORS_LIGHT['text']};
    }}

    .main {{
        background-color: {COLORS_LIGHT['bg']};
        padding: 1.5rem;
    }}

    .stForm {{
        background-color: transparent;
        border: none;
    }}

    /* Card styling */
    .card {{
        background-color: {COLORS_LIGHT['card']};
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid {COLORS_LIGHT['border']};
        margin-bottom: 1.5rem;
    }}

    /* Button styling */
    .stButton > button {{
        background-color: {COLORS_LIGHT['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        background-color: #6D28D9;
        box-shadow: 0 4px 12px rgba(124,58,237,0.15);
    }}

    .stButton > button:disabled {{
        background-color: {COLORS_LIGHT['muted']};
        opacity: 0.6;
    }}

    /* Title styling */
    h1 {{
        color: {COLORS_LIGHT['text']};
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}

    /* Dark Mode - Auto-detect user preference */
    @media (prefers-color-scheme: dark) {{
        body {{
            background-color: {COLORS_DARK['bg']};
            color: {COLORS_DARK['text']};
        }}

        .main {{
            background-color: {COLORS_DARK['bg']};
            padding: 1.5rem;
        }}

        .stForm {{
            background-color: transparent;
        }}

        .card {{
            background-color: {COLORS_DARK['card']};
            border: 1px solid {COLORS_DARK['border']};
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }}

        /* Welcome page card styling in dark mode */
        [data-testid="column"]:has(> div > div > div > div > div > div > div > h3) div:nth-child(2) {{
            background-color: {COLORS_DARK['card']} !important;
            border: 1px solid {COLORS_DARK['border']} !important;
        }}

        .stButton > button {{
            background-color: {COLORS_DARK['primary']};
            color: white;
            border: 1px solid {COLORS_DARK['primary']};
        }}

        .stButton > button:hover {{
            background-color: {COLORS_DARK['accent']};
            color: {COLORS_DARK['bg']};
            border-color: {COLORS_DARK['accent']};
        }}

        .stButton > button:disabled {{
            background-color: {COLORS_DARK['muted']};
            opacity: 0.5;
        }}

        /* Text styling */
        h1, h2, h3 {{
            color: {COLORS_DARK['text']};
        }}

        p {{
            color: {COLORS_DARK['text']};
        }}

        /* Strong/bold text */
        strong {{
            color: {COLORS_DARK['text']};
        }}

        .stInfo {{
            background-color: {COLORS_DARK['assistant_bubble']};
            border-left: 4px solid {COLORS_DARK['primary']};
        }}

        .stCaption {{
            color: {COLORS_DARK['muted']};
        }}

        .stCheckbox {{
            color: {COLORS_DARK['text']};
        }}

        /* Checkbox label styling */
        .stCheckbox label {{
            color: {COLORS_DARK['text']} !important;
        }}

        hr {{
            border-top: 1px solid {COLORS_DARK['border']};
        }}

        .stMetric {{
            background-color: {COLORS_DARK['card']};
        }}

        /* Chat container - dark background like scenario page */
        .chat-container {{
            display: flex !important;
            flex-direction: column;
            gap: 0.75rem;
            padding: 1.5rem;
            background-color: {COLORS_DARK['card']};
            border-radius: 12px;
            min-height: 400px;
            border: 1px solid {COLORS_DARK['border']};
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }}

        .avatar.assistant {{
            background-color: {COLORS_DARK['assistant_bubble']};
            color: white;
        }}

        .avatar.user {{
            background-color: transparent;
            color: {COLORS_DARK['text']};
        }}

        .chat-bubble.assistant {{
            background-color: {COLORS_DARK['assistant_bubble']};
            color: {COLORS_DARK['text']};
            border: 1px solid {COLORS_DARK['border']};
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }}

        .chat-bubble.user {{
            background-color: {COLORS_DARK['user_bubble']};
            color: white;
            font-weight: 500;
        }}

        /* Input area */
        .input-container {{
            display: flex;
            gap: 0.75rem;
            padding: 1rem;
            background-color: {COLORS_DARK['card']};
            border-radius: 12px;
            border: 1px solid {COLORS_DARK['border']};
        }}

        .input-container input {{
            flex: 1;
            padding: 0.75rem;
            border: 1px solid {COLORS_DARK['border']};
            border-radius: 8px;
            font-size: 1rem;
            background-color: {COLORS_DARK['input_bg']};
            color: {COLORS_DARK['text']};
        }}

        .input-container input::placeholder {{
            color: {COLORS_DARK['muted']};
        }}

        /* Loading and indicators */
        .loading-indicator {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 0.5rem;
            color: {COLORS_DARK['muted']};
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }}

        .turn-counter {{
            text-align: center;
            color: {COLORS_DARK['muted']};
            font-size: 0.875rem;
            margin: 1rem 0 0 0;
        }}

        /* Navigation buttons */
        [data-testid="column"] button {{
            border: 1px solid {COLORS_DARK['border']};
            background-color: {COLORS_DARK['card']};
            color: {COLORS_DARK['text']};
        }}

        [data-testid="column"] button:hover {{
            background-color: {COLORS_DARK['primary']};
            color: white;
            border-color: {COLORS_DARK['primary']};
        }}

        /* Demo label styling */
        .demo-label {{
            color: {COLORS_DARK['text']} !important;
        }}

        /* Select/dropdown styling */
        .stSelectbox {{
            color: {COLORS_DARK['text']};
        }}

        /* Slider styling */
        .stSlider {{
            color: {COLORS_DARK['text']};
        }}

        /* Form text inputs */
        .stTextInput input {{
            background-color: {COLORS_DARK['input_bg']};
            color: {COLORS_DARK['text']};
            border: 1px solid {COLORS_DARK['border']};
        }}
    }}

    /* Light Mode - Shared styles */
    h2 {{
        color: {COLORS_LIGHT['text']};
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }}

    h3 {{
        color: {COLORS_LIGHT['text']};
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
        background-color: {COLORS_LIGHT['assistant_bubble']};
        border-radius: 8px;
        border-left: 4px solid {COLORS_LIGHT['primary']};
    }}

    /* Caption styling */
    .stCaption {{
        color: {COLORS_LIGHT['muted']};
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
        border-top: 1px solid {COLORS_LIGHT['border']};
        margin: 2rem 0;
    }}

    /* Metric styling */
    .stMetric {{
        background-color: {COLORS_LIGHT['card']};
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
        background-color: {COLORS_LIGHT['card']};
        border-radius: 12px;
        min-height: 400px;
        border: 1px solid {COLORS_LIGHT['border']};
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
        background-color: {COLORS_LIGHT['assistant_bubble']};
    }}

    .avatar.user {{
        background-color: transparent;
        color: {COLORS_LIGHT['text']};
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
        background-color: {COLORS_LIGHT['assistant_bubble']};
        color: {COLORS_LIGHT['text']};
        border: 1px solid {COLORS_LIGHT['border']};
    }}

    .chat-bubble.user {{
        background-color: {COLORS_LIGHT['user_bubble']};
        color: #FFFFFF;
        font-weight: 500;
    }}

    /* Input area styling */
    .input-container {{
        display: flex;
        gap: 0.75rem;
        padding: 1rem;
        background-color: {COLORS_LIGHT['card']};
        border-radius: 12px;
        border: 1px solid {COLORS_LIGHT['border']};
    }}

    .input-container input {{
        flex: 1;
        padding: 0.75rem;
        border: 1px solid {COLORS_LIGHT['border']};
        border-radius: 8px;
        font-size: 1rem;
    }}

    /* Loading indicator */
    .loading-indicator {{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.5rem;
        color: {COLORS_LIGHT['muted']};
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }}

    /* Turn counter */
    .turn-counter {{
        text-align: center;
        color: {COLORS_LIGHT['muted']};
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

    /* Navigation button row - ensure proper alignment */
    [data-testid="column"] > div:has(> button) {{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 2.5rem;
    }}

    /* Compact navigation buttons */
    [data-testid="column"] button {{
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        min-height: 44px !important;
        border-radius: 8px;
        font-size: 1.25rem;
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['card']};
        color: {COLORS['text']};
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    [data-testid="column"] button:hover {{
        background-color: {COLORS['primary']};
        color: white;
        border-color: {COLORS['primary']};
    }}

    .nav-button-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        min-height: 2.5rem;
    }}

    /* Slider styling - minimal, let Streamlit defaults mostly work */
    .stSlider {{
        padding: 0.5rem 0;
    }}

    /* Demographics section - grid layout */
    .demographics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-top: 1rem;
    }}

    @media (max-width: 768px) {{
        .demographics-grid {{
            grid-template-columns: 1fr;
        }}
    }}

    .demo-label {{
        font-size: 0.85rem !important;
        font-weight: 600;
        margin-bottom: 0.4rem;
        color: {COLORS['text']};
        display: block;
        white-space: normal;
    }}

    /* Welcome page styling - ensure proper contrast in all modes */
    .what-to-expect-item {{
        display: flex;
        gap: 0.75rem;
        align-items: flex-start;
        padding: 0.75rem 0;
    }}

    .what-to-expect-item strong {{
        font-weight: 600;
    }}

    .what-to-expect-item p {{
        margin: 0.25rem 0 0 0;
        font-size: 0.9rem;
    }}

    /* Ensure proper text contrast in dark mode for welcome page */
    @media (prefers-color-scheme: dark) {{
        .what-to-expect-item strong {{
            color: {COLORS_DARK['text']};
        }}

        .what-to-expect-item span:last-of-type {{
            color: {COLORS_DARK['muted']};
        }}

        .what-to-expect-item p {{
            color: {COLORS_DARK['muted']};
        }}
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
    # Detect dark mode - use prefers-color-scheme media query
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; height: 2.5rem;">
        <span style="font-size: 0.875rem; color: {COLORS_LIGHT['muted']}; white-space: nowrap;">
            Step {current} of {total}
        </span>
        <div style="flex-grow: 1; height: 4px; background-color: {COLORS_LIGHT['border']}; border-radius: 2px; overflow: hidden;">
            <div style="width: {(current/total)*100}%; height: 100%; background-color: {COLORS_LIGHT['primary']}; transition: width 0.3s ease;"></div>
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
    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        st.markdown("# 👋 Welcome")
        st.markdown("""
        Thank you for your interest in this study. You will read a short workplace scenario, interact with an AI assistant, and answer a brief questionnaire about your experience.

        **What to expect:**
        """)

        st.markdown(f"""
        <div style="display: grid; gap: 1rem; margin: 1.5rem 0;">
            <div class="what-to-expect-item">
                <span style="font-size: 1.25rem; min-width: 28px; flex-shrink: 0;">📋</span>
                <div style="flex-grow: 1;">
                    <strong>Scenario</strong>
                    <span style="font-size: 0.9rem;"> — 1 minute</span>
                    <p>Read a short workplace situation</p>
                </div>
            </div>
            <div class="what-to-expect-item">
                <span style="font-size: 1.25rem; min-width: 28px; flex-shrink: 0;">💬</span>
                <div style="flex-grow: 1;">
                    <strong>Chat</strong>
                    <span style="font-size: 0.9rem;"> — 5 minutes</span>
                    <p>Have a 3–5 turn conversation with an AI assistant</p>
                </div>
            </div>
            <div class="what-to-expect-item">
                <span style="font-size: 1.25rem; min-width: 28px; flex-shrink: 0;">📝</span>
                <div style="flex-grow: 1;">
                    <strong>Questionnaire</strong>
                    <span style="font-size: 0.9rem;"> — 3 minutes</span>
                    <p>Share your thoughts and background</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Requirements")
        st.markdown(f"""
        <div style="margin: 1.5rem 0;">
            <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem; align-items: flex-start;">
                <span style="color: {COLORS_LIGHT['primary']}; font-weight: 600; flex-shrink: 0; margin-top: 2px;">✓</span>
                <span>You must be at least 18 years old</span>
            </div>
            <div style="display: flex; gap: 0.5rem; align-items: flex-start;">
                <span style="color: {COLORS_LIGHT['primary']}; font-weight: 600; flex-shrink: 0; margin-top: 2px;">✓</span>
                <span>You should have some workplace experience</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="padding: 1.5rem; background-color: {COLORS_LIGHT['card']}; border-radius: 12px; border: 1px solid {COLORS_LIGHT['border']};
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08); height: fit-content; position: sticky; top: 100px;">
            <h3 style="margin: 0 0 1.25rem 0; color: {COLORS_LIGHT['text']}; font-size: 1.1rem;">Ready to participate?</h3>
        </div>
        """, unsafe_allow_html=True)

        consent = st.checkbox("I have read and agree to participate in this study", value=False)

        # Check if DEBUG mode is enabled (via environment variable)
        debug_mode = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        if debug_mode:
            testing_mode = st.checkbox("🧪 Testing mode (developers only)")
            forced_condition = None

            if testing_mode:
                forced_condition = st.radio(
                    "Select condition",
                    ["warm", "competent"],
                    horizontal=True,
                )
        else:
            testing_mode = False
            forced_condition = None

        st.markdown("")  # spacing
        if st.button("Begin Study", use_container_width=True):
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
    col_back, col_progress, col_next = st.columns([0.12, 0.76, 0.12])

    with col_back:
        if st.button("←", key="back_from_vignette", help="Back to consent"):
            st.session_state.stage = "consent"
            st.rerun()

    with col_progress:
        progress_indicator(1)

    with col_next:
        if st.button("→", key="next_from_vignette", help="Begin chat"):
            st.session_state.stage = "chat"
            st.rerun()

    st.markdown("# 📋 Scenario")

    st.markdown(f"""
    <div class="card">
        {st.session_state.vignette_text}
    </div>
    """, unsafe_allow_html=True)

# CHAT PAGE
elif st.session_state.stage == "chat":
    col_back, col_progress, col_next = st.columns([0.12, 0.76, 0.12])

    with col_back:
        if st.button("←", key="back_from_chat", help="Back to scenario"):
            st.session_state.stage = "vignette"
            st.rerun()

    with col_progress:
        progress_indicator(2)

    with col_next:
        if st.session_state.chat_completed:
            if st.button("→", key="next_from_chat", help="Continue to questionnaire"):
                st.session_state.stage = "questionnaire"
                st.rerun()
        else:
            st.write("")

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
        if st.session_state.turns_used >= st.session_state.min_turns and not st.session_state.chat_completed:
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
                        st.session_state.stage = "questionnaire"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Cannot finish yet: {str(e)}")

# QUESTIONNAIRE PAGE
elif st.session_state.stage == "questionnaire":
    col_back, col_progress, col_next = st.columns([0.12, 0.76, 0.12])

    with col_back:
        if st.button("←", key="back_from_questionnaire", help="Back to chat"):
            st.session_state.stage = "chat"
            st.rerun()

    with col_progress:
        progress_indicator(3)

    with col_next:
        st.write("")

    st.markdown("# 📝 Feedback Questionnaire")
    st.markdown("Please answer all required questions.")

    with st.form("questionnaire_form"):
        def likert_item(question: str, key: str) -> int:
            """Render a single Likert scale item with question label and scale."""
            st.markdown(f"""
            <div style="margin-bottom: 2rem; padding: 1.25rem; background-color: {COLORS['card']};
                        border-radius: 12px; border: 1px solid {COLORS['border']};">
                <div style="margin-bottom: 0.75rem;">
                    <p style="margin: 0; font-weight: 600; color: {COLORS['text']}; font-size: 0.95rem;">
                        {question}
                    </p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: {COLORS['muted']};">
                        1 = Strongly disagree &nbsp; • &nbsp; 7 = Strongly agree
                    </p>
                </div>
            """, unsafe_allow_html=True)

            value = st.slider(
                label=question,
                min_value=1,
                max_value=7,
                value=4,
                step=1,
                key=key,
                label_visibility="collapsed"
            )

            st.markdown("</div>", unsafe_allow_html=True)
            return value

        # Perception Section
        st.markdown(f"<h3 style='margin-top: 0; margin-bottom: 1.5rem;'>📊 How did you perceive the assistant?</h3>", unsafe_allow_html=True)

        perc_warm_friendly = likert_item("The assistant seemed friendly.", "perc_warm_friendly")
        perc_warm_understanding = likert_item("The assistant seemed understanding.", "perc_warm_understanding")
        perc_warm_comfortable = likert_item("The assistant made me feel comfortable.", "perc_warm_comfortable")
        perc_struct_direct = likert_item("The assistant seemed direct.", "perc_struct_direct")
        perc_struct_professional = likert_item("The assistant seemed professional.", "perc_struct_professional")
        perc_struct_task_focused = likert_item("The assistant seemed task-focused.", "perc_struct_task_focused")

        st.divider()

        # Safety Section
        st.markdown(f"<h3 style='margin-top: 0; margin-bottom: 1.5rem;'>🛡️ How safe did you feel during the conversation?</h3>", unsafe_allow_html=True)

        psych_safe_1 = likert_item("I felt safe to express any concerns I had.", "psych_safe_1")
        psych_safe_2 = likert_item("I could be honest without worrying about negative consequences.", "psych_safe_2")
        psych_safe_3 = likert_item("I felt comfortable sharing critical feedback.", "psych_safe_3")
        psych_safe_4 = likert_item("I felt able to say what I really thought.", "psych_safe_4")
        psych_safe_5 = likert_item("I did not feel judged when expressing concerns.", "psych_safe_5")

        st.divider()

        # Openness Section
        st.markdown(f"<h3 style='margin-top: 0; margin-bottom: 1.5rem;'>💭 How openly did you respond?</h3>", unsafe_allow_html=True)

        openness_1 = likert_item("I answered the assistant honestly.", "openness_1")
        openness_2 = likert_item("I shared my real thoughts during the conversation.", "openness_2")
        openness_3 = likert_item("I gave concrete details about the situation.", "openness_3")
        openness_4 = likert_item("I held back some things I was thinking.", "openness_4")
        st.caption("(Note: This item will be reverse-scored in analysis)")

        st.divider()

        # Demographics Section
        st.markdown(f"<h3 style='margin-top: 0; margin-bottom: 1.5rem;'>ℹ️ About you</h3>", unsafe_allow_html=True)

        st.markdown('<div class="demographics-grid">', unsafe_allow_html=True)

        # Column 1: AI Experience (Required)
        st.markdown(f"""
        <div>
            <span class="demo-label">Experience with conversational AI <span style="color: #EF4444;">*</span></span>
        </div>
        """, unsafe_allow_html=True)
        ai_exp_selection = st.selectbox(
            label="AI Experience",
            options=["", "1 - No experience", "2", "3", "4", "5", "6", "7 - Very experienced"],
            index=0,
            label_visibility="collapsed"
        )
        if ai_exp_selection and ai_exp_selection != "":
            st.session_state.ai_experience = int(ai_exp_selection.split()[0])
        else:
            st.session_state.ai_experience = None

        # Column 2: Years of work experience (Required)
        st.markdown(f"""
        <div>
            <span class="demo-label">Years of work experience <span style="color: #EF4444;">*</span></span>
        </div>
        """, unsafe_allow_html=True)
        years_options = ["", "0 - Less than 1 year", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11-15", "16-20", "20+"]
        years_selection = st.selectbox(
            label="Years of work experience",
            options=years_options,
            index=0,
            label_visibility="collapsed"
        )
        if years_selection and years_selection != "":
            # Parse the selection and convert to float
            first_part = years_selection.split()[0]
            if first_part == "0":
                years_work_experience = 0.5
            elif first_part == "11-15":
                years_work_experience = 13.0
            elif first_part == "16-20":
                years_work_experience = 18.0
            elif first_part == "20+":
                years_work_experience = 25.0
            else:
                years_work_experience = float(first_part)
        else:
            years_work_experience = None

        # Column 3: Age
        st.markdown(f"""
        <div>
            <span class="demo-label">Age (optional)</span>
        </div>
        """, unsafe_allow_html=True)
        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            step=1,
            value=None,
            label_visibility="collapsed"
        )

        # Column 4: Gender
        st.markdown(f"""
        <div>
            <span class="demo-label">Gender (optional)</span>
        </div>
        """, unsafe_allow_html=True)
        gender = st.selectbox(
            "Gender",
            ["", "Female", "Male", "Prefer not to say"],
            index=0,
            label_visibility="collapsed"
        )

        # Column 5: Industry
        st.markdown(f"""
        <div>
            <span class="demo-label">Industry (optional)</span>
        </div>
        """, unsafe_allow_html=True)
        industry = st.text_input(
            "Industry",
            value="",
            label_visibility="collapsed"
        )

        # Column 6: Job role
        st.markdown(f"""
        <div>
            <span class="demo-label">Job role (optional)</span>
        </div>
        """, unsafe_allow_html=True)
        job_role = st.text_input(
            "Job role",
            value="",
            label_visibility="collapsed"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        submitted = st.form_submit_button(
            "✓ Submit & Complete",
            use_container_width=True
        )

        if submitted:
            # Validate all required fields are answered
            required_items = [
                "perc_warm_friendly", "perc_warm_understanding", "perc_warm_comfortable",
                "perc_struct_direct", "perc_struct_professional", "perc_struct_task_focused",
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
                # Ensure all required fields are integers
                payload = {
                    "participant_id": st.session_state.participant_id,
                    "perc_warm_friendly": int(st.session_state.perc_warm_friendly),
                    "perc_warm_understanding": int(st.session_state.perc_warm_understanding),
                    "perc_warm_comfortable": int(st.session_state.perc_warm_comfortable),
                    "perc_struct_direct": int(st.session_state.perc_struct_direct),
                    "perc_struct_professional": int(st.session_state.perc_struct_professional),
                    "perc_struct_task_focused": int(st.session_state.perc_struct_task_focused),
                    "psych_safe_1": int(st.session_state.psych_safe_1),
                    "psych_safe_2": int(st.session_state.psych_safe_2),
                    "psych_safe_3": int(st.session_state.psych_safe_3),
                    "psych_safe_4": int(st.session_state.psych_safe_4),
                    "psych_safe_5": int(st.session_state.psych_safe_5),
                    "openness_1": int(st.session_state.openness_1),
                    "openness_2": int(st.session_state.openness_2),
                    "openness_3": int(st.session_state.openness_3),
                    "openness_4": int(st.session_state.openness_4),
                    "ai_experience": int(st.session_state.ai_experience),
                    "years_work_experience": float(years_work_experience) if years_work_experience else None,
                    "age": int(age) if age else None,
                    "gender": gender if gender else None,
                    "industry": industry if industry else None,
                    "job_role": job_role if job_role else None,
                }
                data = api_post("/questionnaire", payload)
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
