import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db import SessionLocal
from app.models import Participant

st.set_page_config(page_title="Study Monitor", layout="wide", initial_sidebar_state="collapsed")
st.title("📊 Study Monitor")

# Auto-refresh every 5 seconds
st.markdown(
    """
    <meta http-equiv="refresh" content="5">
    """,
    unsafe_allow_html=True,
)

db = SessionLocal()
participants = db.query(Participant).all()

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Participants", len(participants))
with col2:
    warm = len([p for p in participants if p.condition == "warm"])
    st.metric("Warm Condition", warm)
with col3:
    competent = len([p for p in participants if p.condition == "competent"])
    st.metric("Competent Condition", competent)
with col4:
    completed = len([p for p in participants if p.chat_completed])
    st.metric("Completed", completed)

# Condition balance
st.divider()
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Condition Distribution")
    if len(participants) > 0:
        condition_counts = pd.DataFrame([
            {"Condition": "Warm", "Count": warm, "Percentage": f"{warm/len(participants)*100:.1f}%"},
            {"Condition": "Competent", "Count": competent, "Percentage": f"{competent/len(participants)*100:.1f}%"},
        ])
        st.bar_chart(condition_counts.set_index("Condition")["Count"])

with col2:
    st.metric("Balance Diff", abs(warm - competent))

# Recent participants
st.divider()
st.subheader("Latest Submissions")
recent = sorted(participants, key=lambda x: x.created_at, reverse=True)[:15]

if recent:
    df = pd.DataFrame([
        {
            "Condition": p.condition.capitalize(),
            "Status": "✅ Completed" if p.chat_completed else "⏳ In Progress",
            "Turns": p.total_turns or 0,
            "Words": p.total_user_word_count or 0,
            "Started": p.timestamp_session_start.strftime("%H:%M:%S") if p.timestamp_session_start else "-",
        }
        for p in recent
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No participants yet")

db.close()
st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
