#!/usr/bin/env python3
"""Check if human honesty codings exist in the database."""

import psycopg2

conn = psycopg2.connect(
    host="reseau.proxy.rlwy.net",
    port=34294,
    database="railway",
    user="postgres",
    password="YGaqGysvoNDMMsEakGDgOqkprTGNauHJ",
)

cursor = conn.cursor()

# Count rows in honesty_codings
cursor.execute("SELECT COUNT(*) FROM honesty_codings;")
count = cursor.fetchone()[0]
print(f"[*] Honesty codings in database: {count}")

if count > 0:
    # Show a sample
    cursor.execute("SELECT * FROM honesty_codings LIMIT 3;")
    cols = [desc[0] for desc in cursor.description]
    print(f"\n[*] Columns: {cols}")
    print(f"\n[*] Sample rows:")
    for row in cursor.fetchall():
        print(f"  {row}")
else:
    print("[WARN] No honesty codings found — human data has not been coded yet")

cursor.close()
conn.close()
