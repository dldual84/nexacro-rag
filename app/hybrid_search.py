from app.vector_store import VectorStore
from app.keyword_search import KeywordSearch


class HybridSearch:

    def __init__(self):

        self.vector_store = VectorStore()

        self.keyword_search = KeywordSearch()

    def normalize_scores(
        self,
        results,
        score_key
    ):
        """
        검색 결과 점수를 0~1 범위로 정규화
        """

        if not results:
            return results

        scores = [
            result.get(
                score_key,
                0
            )
            for result in results
        ]

        max_score = max(scores)
        min_score = min(scores)

        # 모든 점수가 같은 경우
        if max_score == min_score:

            for result in results:

                result[
                    f"{score_key}_normalized"
                ] = 1.0

            return results

        for result in results:

            score = result.get(
                score_key,
                0
            )

            normalized = (
                (score - min_score)
                /
                (max_score - min_score)
            )

            result[
                f"{score_key}_normalized"
            ] = normalized

        return results

    def search(
        self,
        query,
        top_k=10,
        vector_k=10,
        keyword_k=10
    ):
        """
        Vector Search + BM25 Hybrid Search
        """

        # ==================================================
        # 1. Vector Search
        # ==================================================

        vector_results = (
            self.vector_store.search(
                query=query,
                top_k=vector_k
            )
        )

        vector_documents = (
            vector_results.get(
                "documents",
                [[]]
            )[0]
        )

        vector_metadatas = (
            vector_results.get(
                "metadatas",
                [[]]
            )[0]
        )

        vector_distances = (
            vector_results.get(
                "distances",
                [[]]
            )[0]
        )

        vector_items = []

        for i, text in enumerate(
            vector_documents
        ):

            metadata = (
                vector_metadatas[i]
                if i < len(vector_metadatas)
                else {}
            )

            distance = (
                vector_distances[i]
                if i < len(vector_distances)
                else None
            )

            if distance is None:

                vector_score = 0.0

            else:

                vector_score = (
                    1.0 /
                    (1.0 + distance)
                )

            document_id = (
                self.make_document_id(
                    text,
                    metadata
                )
            )

            vector_items.append({

                "id": document_id,

                "text": text,

                "metadata": metadata,

                "vector_score": float(
                    vector_score
                )
            })

        # Vector 점수 정규화
        vector_items = (
            self.normalize_scores(
                vector_items,
                "vector_score"
            )
        )

        # ==================================================
        # 2. BM25 Keyword Search
        # ==================================================

        keyword_items = (
            self.keyword_search.search(
                query=query,
                top_k=keyword_k
            )
        )

        # ==================================================
        # 3. Vector + Keyword 결과 통합
        # ==================================================

        combined = {}

        # Vector 결과
        for item in vector_items:

            key = (
                self.make_document_id(
                    item["text"],
                    item["metadata"]
                )
            )

            combined[key] = {

                "id": item["id"],

                "text": item["text"],

                "metadata": item["metadata"],

                "vector_score": item.get(
                    "vector_score_normalized",
                    0.0
                ),

                "keyword_score": 0.0
            }

        # Keyword 결과
        for item in keyword_items:

            key = (
                self.make_document_id(
                    item["text"],
                    item["metadata"]
                )
            )

            if key not in combined:

                combined[key] = {

                    "id": item["id"],

                    "text": item["text"],

                    "metadata": item["metadata"],

                    "vector_score": 0.0,

                    "keyword_score": 0.0
                }

            combined[key][
                "keyword_score"
            ] = item.get(
                "score",
                0.0
            )

        # ==================================================
        # 4. Keyword 점수 정규화
        # ==================================================

        combined_list = list(
            combined.values()
        )

        combined_list = (
            self.normalize_scores(
                combined_list,
                "keyword_score"
            )
        )

        # ==================================================
        # 5. Hybrid Score
        # ==================================================

        VECTOR_WEIGHT = 0.5
        KEYWORD_WEIGHT = 0.5

        for item in combined_list:

            vector_score = item.get(
                "vector_score",
                0.0
            )

            keyword_score = item.get(
                "keyword_score_normalized",
                0.0
            )

            item["hybrid_score"] = (
                vector_score * VECTOR_WEIGHT
                +
                keyword_score * KEYWORD_WEIGHT
            )

        # ==================================================
        # 6. Hybrid Score 기준 정렬
        # ==================================================

        combined_list.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        return combined_list[:top_k]

    @staticmethod
    def make_document_id(
        text,
        metadata
    ):
        """
        Vector 결과와 BM25 결과에서
        동일한 문서를 찾기 위한 Key
        """

        source = metadata.get(
            "source",
            ""
        )

        section = metadata.get(
            "section",
            ""
        )

        title = metadata.get(
            "title",
            ""
        )

        return (
            f"{source}|"
            f"{section}|"
            f"{title}|"
            f"{text}"
        )


if __name__ == "__main__":

    searcher = HybridSearch()

    query = "truevalue"

    results = searcher.search(
        query=query,
        top_k=10
    )

    print("=" * 70)

    print(
        f"검색어: {query}"
    )

    print("=" * 70)

    for i, result in enumerate(
        results,
        start=1
    ):

        metadata = result[
            "metadata"
        ]

        print()
        print("-" * 70)

        print(
            f"{i}. "
            f"Hybrid: "
            f"{result['hybrid_score']:.4f}"
        )

        print(
            f"Vector: "
            f"{result['vector_score']:.4f}"
        )

        print(
            f"Keyword: "
            f"{result['keyword_score']:.4f}"
        )

        print(
            f"Source: "
            f"{metadata.get('source', '')}"
        )

        print(
            f"Section: "
            f"{metadata.get('section', '')}"
        )

        print(
            f"Title: "
            f"{metadata.get('title', '')}"
        )

        print()

        print(
            result["text"][:500]
        )