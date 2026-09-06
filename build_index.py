import json
import os

from app.vector_store import VectorStore


NORMAL_CHUNKS_FILE = os.path.join(
    "data",
    "chunks.json"
)

CHM_CHUNKS_FILE = os.path.join(
    "data",
    "chm_chunks.json"
)


def load_json(path):

    if not os.path.exists(path):

        print(f"파일 없음: {path}")

        return []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def normalize_document(
    document,
    source
):

    text = document.get(
        "text",
        ""
    ).strip()

    if not text:
        return None

    # 기존 chunks.json에 id가 없는 경우도 처리
    original_id = document.get(
        "id"
    )

    if original_id:

        document_id = str(
            original_id
        )

    else:

        document_id = None

    return {
        "id": document_id,
        "source": document.get(
            "source",
            source
        ),
        "section": document.get(
            "section",
            ""
        ),
        "title": document.get(
            "title",
            ""
        ),
        "pages": document.get(
            "pages",
            []
        ),
        "path": document.get(
            "path",
            ""
        ),
        "text": text
    }


def make_unique_id(
    document,
    index,
    source
):

    # source를 ID 앞에 붙여 문서간 충돌 방지
    #
    # 예:
    # nexacro_workbook_000001
    # nexacro_manual_000001

    return (
        f"{source}_"
        f"{index:06d}"
    )


def build_index():

    print("=" * 60)
    print("RAG Index Build")
    print("=" * 60)

    all_documents = []

    # --------------------------------------------------
    # 1. 기존 Nexacro 문서
    # --------------------------------------------------

    normal_chunks = load_json(
        NORMAL_CHUNKS_FILE
    )

    print()
    print(
        f"기존 chunks.json : "
        f"{len(normal_chunks)}개"
    )

    for index, document in enumerate(
        normal_chunks
    ):

        normalized = normalize_document(
            document,
            "nexacro_workbook"
        )

        if normalized is None:
            continue

        # 기존 ID가 있더라도
        # source + index 방식으로 새로 부여
        normalized["id"] = make_unique_id(
            normalized,
            index,
            "nexacro_workbook"
        )

        all_documents.append(
            normalized
        )

    # --------------------------------------------------
    # 2. CHM 문서
    # --------------------------------------------------

    chm_chunks = load_json(
        CHM_CHUNKS_FILE
    )

    print(
        f"CHM chunks.json : "
        f"{len(chm_chunks)}개"
    )

    for index, document in enumerate(
        chm_chunks
    ):

        normalized = normalize_document(
            document,
            "nexacro_manual"
        )

        if normalized is None:
            continue

        normalized["id"] = make_unique_id(
            normalized,
            index,
            "nexacro_manual"
        )

        all_documents.append(
            normalized
        )

    # --------------------------------------------------
    # 중복 ID 최종 확인
    # --------------------------------------------------

    ids = [
        document["id"]
        for document in all_documents
    ]

    if len(ids) != len(set(ids)):

        print()
        print("ERROR: ID 중복 발생")

        return

    print()
    print(
        f"전체 문서 Chunk : "
        f"{len(all_documents)}개"
    )

    # --------------------------------------------------
    # ChromaDB 저장
    # --------------------------------------------------

    store = VectorStore()

    print()
    print(
        f"기존 ChromaDB : "
        f"{store.count()}개"
    )

    # VectorStore.add_documents()가
    # 현재 구조에서는 metadata를 별도로 받는다.
    documents_for_store = []

    for document in all_documents:

        metadata = {
            "source": document["source"],
            "section": document["section"],
            "title": document["title"],
            "pages": str(
                document["pages"]
            ),
            "path": document["path"]
        }

        documents_for_store.append({

            "id": document["id"],

            "text": document["text"],

            "metadata": metadata
        })

    # --------------------------------------------------
    # 한번에 넣기
    # --------------------------------------------------

    BATCH_SIZE = 100

    total = len(
        documents_for_store
    )

    for start in range(
        0,
        total,
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            total
        )

        batch = documents_for_store[
            start:end
        ]

        store.add_documents(
            batch
        )

        print(
            f"Indexed "
            f"{end}/{total}"
        )

    print()
    print("=" * 60)
    print("Index Build 완료")
    print("=" * 60)

    print(
        f"ChromaDB 문서 수 : "
        f"{store.count()}"
    )


if __name__ == "__main__":
    build_index()