#!/usr/bin/env python3
"""Export human data from Railway PostgreSQL to CSV files."""

import psycopg2
import csv
from datetime import datetime

# Connection details from Railway
conn = psycopg2.connect(
    host="reseau.proxy.rlwy.net",
    port=34294,
    database="railway",
    user="postgres",
    password="YGaqGysvoNDMMsEakGDgOqkprTGNauHJ",
)

cursor = conn.cursor()

# Export questionnaire responses
print("[*] Exporting questionnaire_responses...")
cursor.execute("SELECT * FROM questionnaire_responses;")
with open("questionnaires_fresh.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(cursor.fetchall())
print(f"[OK] Wrote questionnaires_fresh.csv")

# Export messages
print("[*] Exporting messages...")
cursor.execute("SELECT * FROM messages;")
with open("messages_fresh.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(cursor.fetchall())
print(f"[OK] Wrote messages_fresh.csv")

# Export participants
print("[*] Exporting participants...")
cursor.execute("SELECT * FROM participants;")
with open("participants_fresh.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([desc[0] for desc in cursor.description])
    writer.writerows(cursor.fetchall())
print(f"[OK] Wrote participants_fresh.csv")

cursor.close()
conn.close()
print("[OK] Done")
