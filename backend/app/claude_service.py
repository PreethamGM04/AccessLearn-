
import re

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.models import UniversalLesson, LessonSection


MODEL_NAME = "google/flan-t5-base"

print("Loading accessibility AI model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

print("Accessibility AI model loaded.")


def _simplify_text(text: str) -> str:
    """Create a simpler version of educational text."""

    if not text.strip():
        return ""

    prompt = f"""
Rewrite the following educational text in simple, clear language
for a student who benefits from easy reading.

Keep the meaning and important facts.
Do not add new information.
Return only the rewritten text.

TEXT:
{text}
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=180,
    )

    return tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    ).strip()


def generate_universal_lesson(
    document_text: str,
    source_filename: str,
    total_pages: int,
    total_words: int,
) -> UniversalLesson:
    """Create an accessible lesson using the free local model."""

    text = document_text.strip()

    if not text:
        raise RuntimeError("No educational content was provided.")

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    paragraphs = paragraphs[:8]

    sections = []

    for index, paragraph in enumerate(paragraphs, start=1):
        simplified = _simplify_text(paragraph)

        sections.append(
            LessonSection(
                section_number=index,
                section_title=f"Section {index}",
                original_content=paragraph,
                easy_reading_content=simplified or paragraph,
            )
        )

    summary_source = paragraphs[0] if paragraphs else text

    if len(summary_source) > 400:
        summary_source = summary_source[:400] + "..."

    return UniversalLesson(
        title="Accessible Learning Lesson",
        subject="General",
        grade_level="Not specified",
        summary=summary_source,
        learning_objectives=[
            "Understand the main ideas in the lesson.",
            "Review important information using accessible content.",
        ],
        vocabulary=[],
        sections=sections,
        source_filename=source_filename,
        total_pages=total_pages,
        total_words=total_words,
    )
