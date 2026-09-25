import fitz
from typing import List
from pathlib import Path

from app.models import (
    ParsedDocument,
    DocumentMetadata,
    PageContent,
    ImageInfo,
)


def parse_pdf(
    file_bytes: bytes,
    filename: str,
    images_dir: Path,
) -> ParsedDocument:
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    raw_meta = doc.metadata
    total_pages = len(doc)

    pages: List[PageContent] = []
    total_words = 0
    extracted_images_count = 0

    for page_num in range(total_pages):
        page = doc.load_page(page_num)

        text = page.get_text()
        words = text.split()
        word_count = len(words)

        total_words += word_count

        images: List[ImageInfo] = []

        try:
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list, start=1):
                xref = img[0]

                try:
                    pix = fitz.Pixmap(doc, xref)

                    if pix.n > 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)

                    img_filename = (
                        f"page{page_num + 1}_img{img_index}.png"
                    )

                    img_path = images_dir / img_filename
                    pix.save(str(img_path))

                    images.append(
                        ImageInfo(
                            page_number=page_num + 1,
                            image_index=img_index,
                            width=pix.width,
                            height=pix.height,
                            extension="png",
                            filename=img_filename,
                            url=f"/images/{img_filename}",
                        )
                    )

                    extracted_images_count += 1

                except Exception:
                    continue

        except Exception:
            pass

        pages.append(
            PageContent(
                page_number=page_num + 1,
                text=text.strip(),
                word_count=word_count,
                images=images,
            )
        )

    doc.close()

    return ParsedDocument(
        filename=filename,
        metadata=DocumentMetadata(
            title=raw_meta.get("title") or None,
            author=raw_meta.get("author") or None,
            subject=raw_meta.get("subject") or None,
            creator=raw_meta.get("creator") or None,
            creation_date=raw_meta.get("creationDate") or None,
            total_pages=total_pages,
        ),
        pages=pages,
        total_words=total_words,
        extracted_images_count=extracted_images_count,
    )
