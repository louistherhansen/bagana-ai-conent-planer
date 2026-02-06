"""Quick test: LiteLLM + OpenRouter with .env. Run from project root: python scripts/test-openrouter-litellm.py"""
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

def clean_key(val):
    if not val:
        return ""
    s = val.strip().strip("'\"").replace("\r", "").replace("\n", "").replace("\uFEFF", "").strip()
    return "".join(c for c in s if not c.isspace())

key = clean_key(os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY"))
os.environ["OPENROUTER_API_KEY"] = key
print("Key present:", bool(key), "len:", len(key) if key else 0)

if key:
    import litellm
    try:
        r = litellm.completion(model="openrouter/openai/gpt-4o-mini", messages=[{"role": "user", "content": "Say hi in one word"}])
        print("OK:", r.choices[0].message.content[:80])
    except Exception as e:
        print("Error:", e)
