import json
import os
import re

from rank_bm25 import BM25Okapi


NORMAL_CHUNKS_FILE = os.path.join(
    "data",
    "chunks.json"
)

CHM_CHUNKS_FILE = os.path.join(
    "data",
    "chm_chunks.json"
)


def tokenize(text):
    """
    Nexacro 문서 검색용 토큰화

    한글
    영문
    영문+숫자
    숫자
    underscore가 포함된 API / 변수명
    """

    if not text:
        return []

    text = text.lower()

    tokens = re.findall(
        r"[가-힣]+|[a-zA-Z_][a-zA-Z0-9_]*|\d+",
        text
    )

    return tokens


def load_json(path):

    if not os.path.exists(path):
        return []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


class KeywordSearch:

    def __init__(self):

        # 기존 문서
        normal_chunks = load_json(
            NORMAL_CHUNKS_FILE
        )

        # CHM 문서
        chm_chunks = load_json(
            CHM_CHUNKS_FILE
        )

        self.documents = []

        # 기존 문서 추가
        for index, document in enumerate(
            normal_chunks
        ):

            document = document.copy()

            document.setdefault(
                "source",
                "nexacro_workbook"
            )

            document.setdefault(
                "id",
                f"nexacro_workbook_{index:06d}"
            )

            self.documents.append(
                document
            )

        # CHM 문서 추가
        for index, document in enumerate(
            chm_chunks
        ):

            document = document.copy()

            document.setdefault(
                "source",
                "nexacro_manual"
            )

            document.setdefault(
                "id",
                f"nexacro_manual_{index:06d}"
            )

            self.documents.append(
                document
            )

        # BM25 검색용 Corpus
        self.tokenized_corpus = []

        for document in self.documents:

            text = document.get(
                "text",
                ""
            )

            title = document.get(
                "title",
                ""
            )

            section = document.get(
                "section",
                ""
            )

            searchable_text = (
                f"{title}\n"
                f"{section}\n"
                f"{text}"
            )

            tokens = tokenize(
                searchable_text
            )

            self.tokenized_corpus.append(
                tokens
            )

        # BM25 생성
        if self.tokenized_corpus:

            self.bm25 = BM25Okapi(
                self.tokenized_corpus
            )

        else:

            self.bm25 = None

    def search(
        self,
        query,
        top_k=5
    ):

        if self.bm25 is None:
            return []

        query_tokens = tokenize(
            query
        )

        if not query_tokens:
            return []

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indexes[:top_k]:

            document = self.documents[
                index
            ]

            results.append({

                "id": document.get(
                    "id",
                    ""
                ),

                "text": document.get(
                    "text",
                    ""
                ),

                "metadata": {
                    "source": document.get(
                        "source",
                        ""
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
                    )
                },

                "score": float(
                    scores[index]
                )
            })

        return results


if __name__ == "__main__":

    searcher = KeywordSearch()

    print(
        f"전체 문서 수: "
        f"{len(searcher.documents)}"
    )

    query = "truevalue"

    results = searcher.search(
        query,
        top_k=10
    )

    print()
    print(
        f"검색어: {query}"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        metadata = result["metadata"]

        print()
        print("-" * 60)

        print(f"{i}.")
        print(
            f"source  : "
            f"{metadata['source']}"
        )

        print(
            f"section : "
            f"{metadata['section']}"
        )

        print(
            f"title   : "
            f"{metadata['title']}"
        )

        print(
            f"score   : "
            f"{result['score']:.4f}"
        )

        print(
            result["text"][:300]
        )