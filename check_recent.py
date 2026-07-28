import sys
from datetime import datetime, timedelta

sys.path.insert(0, 'backend')

from app.db import SessionLocal
from app.models import Participant, Message

db = SessionLocal()

print("=== RECENT PARTICIPANTS (last 10 min) ===")
recent_participants = db.query(Participant).filter(
    Participant.created_at > datetime.utcnow() - timedelta(minutes=10)
).order_by(Participant.created_at.desc()).all()

for p in recent_participants:
    print(f"ID: {p.participant_id[:8]} | Condition: {p.condition:9} | Turns: {p.total_turns} | Completed: {p.chat_completed} | Stage: {p.completion_stage} | Created: {p.created_at.strftime('%H:%M:%S')}")

print(f"\nTotal: {len(recent_participants)} participants\n")

print("=== RECENT MESSAGES (last 10 min) ===")
recent_messages = db.query(Message).filter(
    Message.timestamp_created > datetime.utcnow() - timedelta(minutes=10)
).order_by(Message.timestamp_created.desc()).all()

for m in recent_messages:
    content_preview = m.content[:60].replace('\n', ' ') if m.content else ''
    print(f"Turn {m.turn_index} | {m.role:9} | {content_preview}... | {m.timestamp_created.strftime('%H:%M:%S')}")

print(f"\nTotal: {len(recent_messages)} messages")

db.close()
