#!/usr/bin/env python3
"""Quick test to verify API keys are valid."""

import os
from dotenv import load_dotenv
import anthropic
import openai

# Load .env
load_dotenv('backend/.env')

print("=" * 70)
print("API Key Validation Test")
print("=" * 70)

# Test Anthropic
print("\n[1] Testing Anthropic API key...")
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_key:
    print("[FAIL] ANTHROPIC_API_KEY not found in .env")
else:
    print(f"[OK] Found key: {anthropic_key[:20]}...")
    try:
        client = anthropic.Anthropic(api_key=anthropic_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("[OK] Anthropic API key is VALID")
    except Exception as e:
        print(f"[FAIL] Anthropic API key is INVALID: {e}")

# Test OpenAI
print("\n[2] Testing OpenAI API key...")
openai_key = os.getenv('OPENAI_API_KEY')
if not openai_key:
    print("[FAIL] OPENAI_API_KEY not found in .env")
else:
    print(f"[OK] Found key: {openai_key[:20]}...")
    try:
        client = openai.OpenAI(api_key=openai_key)
        msg = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("[OK] OpenAI API key is VALID")
    except Exception as e:
        print(f"[FAIL] OpenAI API key is INVALID: {e}")

print("\n" + "=" * 70)
print("Test complete. Both keys must show [OK] before running generation.")
print("=" * 70)
