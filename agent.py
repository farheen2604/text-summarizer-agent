import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

try:
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
except Exception:
    logging.basicConfig(level=logging.INFO)

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.5-flash")

def prepare_text_for_summary(tool_context: ToolContext, input_text: str) -> dict:
    """Validates and stores the user's raw input text into agent state."""
    text = input_text.strip()
    if not text:
        return {"status": "error", "message": "Input text is empty."}
    if len(text) < 30:
        return {"status": "error", "message": "Input text is too short. Please provide at least a sentence or two."}
    tool_context.state["RAW_TEXT"] = text
    word_count = len(text.split())
    logging.info(f"[prepare_text_for_summary] Stored {word_count} words into state.")
    return {"status": "success", "word_count": word_count}

root_agent = Agent(
    name="text_summarizer",
    model=model_name,
    description="Accepts any block of text and returns a structured summary with TL;DR, key points, and tone.",
    instruction="""
You are a precise Text Summarization Agent.

STEP 1 — When the user sends text, call 'prepare_text_for_summary' with the full input text.
STEP 2 — If tool returns status "error", relay the message and ask for valid text.
STEP 3 — If tool returns status "success", produce a summary in this exact format:

---
**TL;DR:** <One sentence, under 25 words.>

**Key Points:**
- <Point 1>
- <Point 2>
- <Point 3>
- <Point 4 if warranted>
- <Point 5 if warranted>

**Tone:** <One word: Formal / Informational / Technical / Conversational / Persuasive>
---

Rules:
- TL;DR must be ONE sentence under 25 words.
- Key Points: minimum 3, maximum 5.
- No commentary outside the format above.
""",
    tools=[prepare_text_for_summary],
)
