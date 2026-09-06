import re


TOKEN_PATTERN = re.compile(
    r"[가-힣]+|[a-zA-Z_][a-zA-Z0-9_]*|\d+"
)


def tokenize(text):

    if not text:
        return []

    return [
        token.lower()
        for token in TOKEN_PATTERN.findall(
            str(text)
        )
    ]


class DocumentRanker:

    def __init__(self):
        pass

    def calculate_score(
        self,
        query,
        document
    ):

        metadata = document.get(
            "metadata",
            {}
        )

        title = str(
            metadata.get(
                "title",
                ""
            )
        )

        section = str(
            metadata.get(
                "section",
                ""
            )
        )

        text = str(
            document.get(
                "text",
                ""
            )
        )

        query_tokens = tokenize(
            query
        )

        title_tokens = set(
            tokenize(title)
        )

        section_tokens = set(
            tokenize(section)
        )

        text_tokens = set(
            tokenize(text)
        )

        if not query_tokens:
            return 0

        keyword_match = 0
        title_match = 0
        section_match = 0

        for token in query_tokens:

            if token in text_tokens:
                keyword_match += 1

            if token in title_tokens:
                title_match += 1

            if token in section_tokens:
                section_match += 1

        # 중복 토큰 방지
        query_count = max(
            len(set(query_tokens)),
            1
        )

        keyword_ratio = (
            keyword_match
            / query_count
        )

        title_ratio = (
            title_match
            / query_count
        )

        section_ratio = (
            section_match
            / query_count
        )

        hybrid_score = document.get(
            "hybrid_score",
            0
        )

        vector_score = document.get(
            "vector_score",
            0
        )

        keyword_score = document.get(
            "keyword_score",
            0
        )

        score = 0

        score += (
            hybrid_score * 0.45
        )

        score += (
            vector_score * 0.10
        )

        score += (
            keyword_score * 0.10
        )

        score += (
            keyword_ratio * 0.15
        )

        score += (
            title_ratio * 0.15
        )

        score += (
            section_ratio * 0.05
        )

        return score

    def rank(
        self,
        query,
        documents,
        top_k=5
    ):

        scored = []

        for document in documents:

            score = self.calculate_score(
                query,
                document
            )

            document["ranking_score"] = score

            scored.append(
                document
            )

        scored.sort(
            key=lambda item:
                item.get(
                    "ranking_score",
                    0
                ),
            reverse=True
        )

        return scored[:top_k]


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