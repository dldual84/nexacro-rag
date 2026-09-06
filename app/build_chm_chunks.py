import os
import json
import re


INPUT_FILE = os.path.join(
    "data",
    "chm_parsed.json"
)

OUTPUT_FILE = os.path.join(
    "data",
    "chm_chunks.json"
)

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def clean_text(text):

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def split_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):

    text = clean_text(text)

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )

        chunk = text[start:end]

        # 가능하면 문장 단위로 자르기
        if end < text_length:

            last_newline = chunk.rfind("\n")

            if last_newline > chunk_size * 0.5:

                end = start + last_newline
                chunk = text[start:end]

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def build_chunks():

    if not os.path.exists(INPUT_FILE):

        print("파싱 결과 파일이 없습니다.")
        print(f"경로: {INPUT_FILE}")
        print()
        print("먼저 실행하세요:")
        print("python -m app.parse_chm")

        return

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        documents = json.load(f)

    chunks = []

    for document_index, document in enumerate(
        documents
    ):

        text = document.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        source = document.get(
            "source",
            "nexacro_manual"
        )

        title = document.get(
            "title",
            ""
        )

        path = document.get(
            "path",
            ""
        )

        text_chunks = split_text(
            text
        )

        for chunk_index, chunk_text in enumerate(
            text_chunks
        ):

            # 반드시 전체적으로 유일해야 한다.
            chunk_id = (
                f"chm_"
                f"{document_index}_"
                f"{chunk_index}"
            )

            chunks.append({

                "id": chunk_id,

                "source": source,

                "section": title,

                "title": title,

                "pages": [],

                "path": path,

                "text": chunk_text
            })

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 60)
    print("CHM Chunk 생성 완료")
    print("=" * 60)

    print(f"원본 HTML : {len(documents)}개")
    print(f"Chunk     : {len(chunks)}개")
    print(f"출력      : {OUTPUT_FILE}")

    print()

    for chunk in chunks[:5]:

        print("-" * 60)
        print(f"ID      : {chunk['id']}")
        print(f"Source  : {chunk['source']}")
        print(f"Title   : {chunk['title']}")
        print(f"Path    : {chunk['path']}")
        print(f"Text    : {chunk['text'][:300]}")


if __name__ == "__main__":
    build_chunks()