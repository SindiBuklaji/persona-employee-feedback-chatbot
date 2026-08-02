#!/usr/bin/env python3
"""List all tables in the Railway database."""

import psycopg2

conn = psycopg2.connect(
    host="reseau.proxy.rlwy.net",
    port=34294,
    database="railway",
    user="postgres",
    password="YGaqGysvoNDMMsEakGDgOqkprTGNauHJ",
)

cursor = conn.cursor()

# List all tables
cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")

print("[*] Tables in 'public' schema:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.close()
conn.close()
