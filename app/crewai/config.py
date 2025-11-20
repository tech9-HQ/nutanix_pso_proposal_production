from __future__ import annotations
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Use gpt-4o (best) or gpt-4o-mini (cheaper but still good)
# gpt-4.1-mini does NOT exist!
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env file")

# Configure LLM with proper settings for proposal generation
openai_llm = LLM(
    model=OPENAI_MODEL_NAME,
    api_key=OPENAI_API_KEY,
    temperature=0.7,  # Creative but not random (0.0-1.0 scale)
    max_tokens=8000,  # Allow long outputs for comprehensive proposals
    # Note: gpt-4o supports up to 16K output tokens
    # gpt-4o-mini supports up to 16K output tokens
)

print(f"✓ LLM configured: {OPENAI_MODEL_NAME} (temp=0.7, max_tokens=8000)")