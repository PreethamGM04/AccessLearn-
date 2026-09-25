import json
import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv

from app.models import UniversalLesson


load_dotenv()


ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


if not ANTHROPIC_API_KEY:
    raise RuntimeError(
        "ANTHROPIC_API_KEY is not set. "
        "Add it to your environment before starting the server."
    )


client = Anthropic(api_key=ANTHROPIC_API_KEY)


SYSTEM_PROMPT = """
You are an accessibility-focused EdTech content transformation agent.

Your task is to transform teacher-provided educational content into a
structured lesson that can support different learners.

Preserve the meaning of the original educational content.

Create:
- a clear lesson title
- subject
- grade level
- concise summary
- learning objectives
- important vocabulary with simple definitions
- lesson sections
- an easy-reading version of each section

Accessibility principles:
- Use clear and simple language.
- Keep important technical terms.
- Explain difficult concepts without removing essential meaning.
- Make easy-reading content suitable for learners who benefit from
  simplified language.
- Do not invent facts that are not supported by the source content.

IMPORTANT:
Return ONLY valid JSON.
Do not use Markdown.
Do not wrap the JSON in ```json code fences.
Do not add explanations before or after the JSON.

The JSON must match this structure exactly:

{
  "title": "string",
  "subject": "string",
  "grade_level": "string",
  "summary": "string",
  "learning_objectives": ["string"],
  "vocabulary": [
    {
      "term": "string",
      "definition": "string"
    }
  ],
  "sections": [
    {
      "section_number": 1,
      "section_title": "string",
      "original_content": "string",
      "easy_reading_content": "string"
    }
  ],
  "source_filename": "string",
  "total_pages": 0,
  "total_words": 0
}
"""


def _clean_json_text(text: str) -> str:
    """
    Remove accidental Markdown code fences from Claude's response.
    """
    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return text.strip()


def generate_universal_lesson(
    document_text: str,
    source_filename: str,
    total_pages: int,
    total_words: int,
) -> UniversalLesson:
    """
    Send extracted educational content to Claude and convert
    the response into a validated UniversalLesson.
    """

    prompt = f"""
Transform the following educational document into an accessible
UniversalLesson.

Source filename: {source_filename}
Total pages: {total_pages}
Total words: {total_words}

DOCUMENT CONTENT:
-----------------
{document_text}
-----------------

Return ONLY the JSON object matching the required schema.
"""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    if not response.content:
        raise RuntimeError("Claude returned an empty response.")

    response_text = response.content[0].text
    cleaned_text = _clean_json_text(response_text)

    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Claude returned invalid JSON: {exc}"
        ) from exc

    # Defensive handling in case Claude returns:
    # {"lesson": {...}}
    if isinstance(data, dict) and "lesson" in data:
        data = data["lesson"]

    try:
        lesson = UniversalLesson.model_validate(data)
    except Exception as exc:
        raise RuntimeError(
            f"Claude response did not match the UniversalLesson schema: {exc}"
        ) from exc

    return lesson
