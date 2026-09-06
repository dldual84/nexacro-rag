import re
import json

from app.chunker import extract_sections


SECTION_PATTERN = re.compile(
    r"^\d+\.\d+(?:\.\d+)?$"
)


PDF_PATH = "data/nexacro_17_workbook.pdf"
CHUNK_PATH = "data/chunks.json"


def main():

    print("=" * 70)
    print("Nexacro 17 Chunker Test")
    print("=" * 70)

    # --------------------------------------------------
    # PDF 읽기
    # --------------------------------------------------

    import fitz

    doc = fitz.open(PDF_PATH)

    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()

        pages.append({
            "page": page_number,
            "text": text
        })

    doc.close()

    # --------------------------------------------------
    # Section 추출
    # --------------------------------------------------

    sections = extract_sections(
        pages,
        min_page=1
    )

    print()

    print("=" * 70)
    print("Section 추출 결과")
    print("=" * 70)

    for section in sections:

        print()

        print("=" * 70)
        print(f"Section: {section['section']}")
        print(f"Title: {section['title']}")
        print(f"Pages: {section['pages']}")
        print("-" * 70)

        print(section["text"][:1000])

    print()

    print("=" * 70)
    print(f"발견 Section 수: {len(sections)}")
    print("=" * 70)

    # --------------------------------------------------
    # chunks.json 저장
    # --------------------------------------------------

    with open(CHUNK_PATH, "w", encoding="utf-8") as f:

        json.dump(
            sections,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("Chunk 저장 완료")
    print("=" * 70)
    print(f"파일: {CHUNK_PATH}")
    print(f"Chunk 수: {len(sections)}")

    # --------------------------------------------------
    # truevalue 검색 테스트
    # --------------------------------------------------

    keyword = "truevalue"

    print()

    print("=" * 70)
    print(f"키워드 검색: {keyword}")
    print("=" * 70)

    found = []

    for section in sections:

        full_text = (
            section["section"]
            + "\n"
            + section["title"]
            + "\n"
            + section["text"]
        )

        if keyword.lower() in full_text.lower():
            found.append(section)

    print()

    print("=" * 70)
    print("Section 검색 결과")
    print("=" * 70)

    for section in found:

        print()

        print("=" * 70)
        print(f"Section: {section['section']}")
        print(f"Title: {section['title']}")
        print(f"Pages: {section['pages']}")
        print("-" * 70)

        print(section["text"])

    print()

    print("=" * 70)
    print(f"발견 Section 수: {len(found)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
