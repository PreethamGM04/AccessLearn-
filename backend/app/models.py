from pydantic import BaseModel
from typing import List, Optional


class VocabularyItem(BaseModel):
    term: str
    definition: str


class LessonSection(BaseModel):
    section_number: int
    section_title: str
    original_content: str
    easy_reading_content: str


class UniversalLesson(BaseModel):
    title: str
    subject: str
    grade_level: str
    summary: str
    learning_objectives: List[str] = []
    vocabulary: List[VocabularyItem] = []
    sections: List[LessonSection] = []
    source_filename: Optional[str] = None
    total_pages: Optional[int] = None
    total_words: Optional[int] = None
