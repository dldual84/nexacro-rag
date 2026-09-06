import re
from app.hybrid_search import HybridSearch


class DocumentRanker:

    def __init__(self):
        pass

    # --------------------------------------------------
    # 질문에서 검색용 토큰 추출
    # --------------------------------------------------
    def tokenize(self, text):

        text = text.lower()

        tokens = re.findall(
            r"[가-힣]+|[a-zA-Z_][a-zA-Z0-9_]*|\d+(?:\.\d+)?",
            text
        )

        return tokens

    # --------------------------------------------------
    # API / 속성명 추출
    #
    # 예:
    # truevalue
    # falsevalue
    # isChecked
    # replace
    # getColumn
    # --------------------------------------------------
    def extract_api_tokens(self, text):

        tokens = self.tokenize(text)

        api_tokens = []

        for token in tokens:

            if re.fullmatch(
                r"[a-zA-Z_][a-zA-Z0-9_]*",
                token
            ):
                api_tokens.append(token.lower())

        return api_tokens

    # --------------------------------------------------
    # 질문 토큰과 문서 정확한 토큰 일치 점수
    # --------------------------------------------------
    def keyword_match_score(self, query, document):

        query_tokens = self.tokenize(query)

        if not query_tokens:
            return 0.0

        text = document.get("text", "").lower()

        if not text:
            return 0.0

        matched = 0

        for token in query_tokens:

            if token in text:
                matched += 1

        return matched / len(query_tokens)

    # --------------------------------------------------
    # 제목 일치 점수
    # --------------------------------------------------
    def title_match_score(self, query, document):

        query_tokens = self.tokenize(query)

        if not query_tokens:
            return 0.0

        metadata = document.get("metadata", {})

        title = str(
            metadata.get("title", "")
        ).lower()

        if not title:
            return 0.0

        matched = 0

        for token in query_tokens:

            if token in title:
                matched += 1

        return matched / len(query_tokens)

    # --------------------------------------------------
    # Section 일치 점수
    # --------------------------------------------------
    def section_match_score(self, query, document):

        metadata = document.get("metadata", {})

        section = str(
            metadata.get("section", "")
        ).lower()

        if not section:
            return 0.0

        query_lower = query.lower()

        if section in query_lower:
            return 1.0

        return 0.0

    # --------------------------------------------------
    # API 이름 정확한 일치
    # --------------------------------------------------
    def api_match_score(self, query, document):

        query_api = self.extract_api_tokens(query)

        if not query_api:
            return 0.0

        text = document.get("text", "").lower()

        matched = 0

        for api in query_api:

            pattern = r"\b" + re.escape(api) + r"\b"

            if re.search(pattern, text):

                matched += 1

        return matched / len(query_api)

    # --------------------------------------------------
    # 최종 Ranking Score
    # --------------------------------------------------
    def calculate_score(self, query, document):

        vector_score = float(
            document.get("vector_score", 0.0)
        )

        keyword_score = float(
            document.get("keyword_score", 0.0)
        )

        hybrid_score = float(
            document.get("hybrid_score", 0.0)
        )

        keyword_match = self.keyword_match_score(
            query,
            document
        )

        title_match = self.title_match_score(
            query,
            document
        )

        section_match = self.section_match_score(
            query,
            document
        )

        api_match = self.api_match_score(
            query,
            document
        )

        # --------------------------------------------------
        # Ranking 가중치
        # --------------------------------------------------
        score = (

            hybrid_score * 0.55

            + vector_score * 0.10

            + keyword_score * 0.10

            + keyword_match * 0.10

            + title_match * 0.10

            + api_match * 0.05
        )

        # Section 직접 지정 보너스
        if section_match > 0:

            score += 0.10

        return score

    # --------------------------------------------------
    # 문서 Ranking
    # --------------------------------------------------
    def rank(
        self,
        query,
        documents,
        top_k=5
    ):

        ranked_documents = []

        for document in documents:

            document = document.copy()

            ranking_score = self.calculate_score(
                query,
                document
            )

            document["ranking_score"] = ranking_score

            ranked_documents.append(
                document
            )

        ranked_documents.sort(
            key=lambda x: x["ranking_score"],
            reverse=True
        )

        return ranked_documents[:top_k]


# --------------------------------------------------
# 편의 함수
# --------------------------------------------------
def rank_documents(
    query,
    documents,
    top_k=5
):

    ranker = DocumentRanker()

    return ranker.rank(
        query=query,
        documents=documents,
        top_k=top_k
    )


# --------------------------------------------------
# Ranking 테스트
# --------------------------------------------------
if __name__ == "__main__":

    from app.hybrid_search import HybridSearch

    query = "CheckBox의 truevalue 속성은 무엇인가?"

    searcher = HybridSearch()

    print("=" * 70)
    print("Nexacro 17 Ranking Test")
    print("=" * 70)

    print(f"\n질문: {query}")

    documents = searcher.search(
        query=query,
        top_k=10
    )

    ranked = rank_documents(
        query=query,
        documents=documents,
        top_k=5
    )

    print("\n[Ranking 결과]")

    for i, document in enumerate(
        ranked,
        start=1
    ):

        metadata = document.get(
            "metadata",
            {}
        )

        print(
            f"\n{i}. "
            f"Ranking={document.get('ranking_score', 0):.4f}"
        )

        print(
            f"   Hybrid={document.get('hybrid_score', 0):.4f}"
        )

        print(
            f"   Vector={document.get('vector_score', 0):.4f}"
        )

        print(
            f"   Keyword={document.get('keyword_score', 0):.4f}"
        )

        print(
            f"   Source={metadata.get('source', '')}"
        )

        print(
            f"   Section={metadata.get('section', '')}"
        )

        print(
            f"   Title={metadata.get('title', '')}"
        )

        text = document.get(
            "text",
            ""
        )

        print(
            f"   Text={text[:300].replace(chr(10), ' ')}"
        )