import pymupdf

from app.chunker import split_into_sections
from app.vector_store import VectorStore


PDF_PATH = "data/nexacro_17_workbook.pdf"


def load_pdf():
    doc = pymupdf.open(PDF_PATH)

    pages = []

    for page_number, page in enumerate(doc):
        text = page.get_text().strip()

        if not text:
            continue

        pages.append(
            {
                "page": page_number + 1,
                "text": text,
            }
        )

    return pages


def build_chunks(pages):

    chunks = []

    for page in pages:

        sections = split_into_sections(
            page["text"]
        )

        for index, section in enumerate(sections):

            if not section["text"]:
                continue

            chunk_id = (
                f"nexacro_"
                f"{page['page']}_"
                f"{section['section'] or 'unknown'}_"
                f"{index}"
            )

            chunks.append(
                {
                    "id": chunk_id,

                    "text": section["text"],

                    "metadata": {
                        "document": "컴포넌트 활용 워크북",
                        "version": "17.1.2.200",
                        "page": page["page"],
                        "section": section["section"] or "",
                        "title": section["title"] or "",
                    },
                }
            )

    return chunks


def main():

    print("=" * 60)
    print("Nexacro PDF RAG Ingestion")
    print("=" * 60)

    print("\n[1] PDF 읽는 중...")

    pages = load_pdf()

    print("페이지 수:", len(pages))

    print("\n[2] Chunk 생성 중...")

    chunks = build_chunks(pages)

    print("Chunk 수:", len(chunks))

    print("\n[3] Ollama Embedding + ChromaDB 저장 중...")

    vector_store = VectorStore()

    batch_size = 50

    for start in range(0, len(chunks), batch_size):

        batch = chunks[start:start + batch_size]

        vector_store.add_documents(batch)

        print(
            f"저장 완료: "
            f"{min(start + batch_size, len(chunks))}"
            f" / "
            f"{len(chunks)}"
        )

    print("\n[4] 완료")

    print(
        "ChromaDB 문서 수:",
        vector_store.count()
    )


if __name__ == "__main__":
    main()