from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models import ParsedDocument, UniversalLesson
from app.parser import parse_pdf
from app.claude_service import generate_universal_lesson


app = FastAPI(
    title="One Curriculum. Every Learner.",
    description="Accessibility-first AI education platform",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path("uploads")
IMAGES_DIR = Path("images")

UPLOAD_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)


app.mount(
    "/images",
    StaticFiles(directory=str(IMAGES_DIR)),
    name="images",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "one-curriculum-backend",
    }


@app.post(
    "/api/v1/upload-pdf",
    response_model=ParsedDocument,
)
async def upload_pdf(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    contents = await file.read()

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        parsed = parse_pdf(
            contents,
            file.filename,
            IMAGES_DIR,
        )

        return parsed

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF parsing failed: {str(e)}",
        )


@app.post(
    "/api/v1/process-lesson",
    response_model=UniversalLesson,
)
async def process_lesson(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    contents = await file.read()

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        parsed = parse_pdf(
            contents,
            file.filename,
            IMAGES_DIR,
        )

        document_text = "\n\n".join(
            f"Page {page.page_number}\n{page.text}"
            for page in parsed.pages
            if page.text.strip()
        )

        if not document_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in the PDF.",
            )

        lesson = generate_universal_lesson(
            document_text=document_text,
            source_filename=parsed.filename,
            total_pages=parsed.metadata.total_pages,
            total_words=parsed.total_words,
        )

        return lesson

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI lesson processing failed: {str(e)}",
        )
