from pydantic import BaseModel
from typing import List, Optional


class ImageInfo(BaseModel):
    page_number: int
    image_index: int
    width: int
    height: int
    extension: str
    filename: str
    url: str


class PageContent(BaseModel):
    page_number: int
    text: str
    word_count: int
    images: List[ImageInfo]


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    creation_date: Optional[str] = None
    total_pages: int


class ParsedDocument(BaseModel):
    filename: str
    metadata: DocumentMetadata
    pages: List[PageContent]
    total_words: int
    extracted_images_count: int


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
