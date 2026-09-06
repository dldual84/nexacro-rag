from app.vector_store import VectorStore
import re


def tokenize(text):
    """
    검색어를 간단한 토큰으로 분리한다.
    한글, 영문, 숫자를 기준으로 처리한다.
    """

    if not text:
        return []

    return re.findall(
        r"[가-힣A-Za-z0-9_]+",
        text.lower()
    )


def keyword_score(query, document):
    """
    질문의 키워드가 문서에 얼마나 포함되어 있는지 계산한다.
    """

    query_tokens = tokenize(query)
    document_lower = document.lower()

    if not query_tokens:
        return 0.0

    score = 0.0

    for token in query_tokens:

        if token in document_lower:

            # 정확한 API명/속성명처럼 긴 단어를 조금 더 높게 평가
            if len(token) >= 5:
                score += 2.0
            else:
                score += 1.0

    return score


def search(query, top_k=3):

    store = VectorStore()

    # Vector 검색은 조금 더 많이 가져온다.
    vector_results = store.search(
        query=query,
        top_k=10
    )

    documents = vector_results.get(
        "documents",
        [[]]
    )[0]

    metadatas = vector_results.get(
        "metadatas",
        [[]]
    )[0]

    distances = vector_results.get(
        "distances",
        [[]]
    )[0]

    candidates = []

    for i, document in enumerate(documents):

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        distance = (
            distances[i]
            if i < len(distances)
            else None
        )

        # Vector 점수
        #
        # distance가 작을수록 유사함
        # 따라서 1 / (1 + distance) 형태로 변환
        if distance is not None:
            vector_score = 1.0 / (1.0 + distance)
        else:
            vector_score = 0.0

        # Keyword 점수
        k_score = keyword_score(
            query,
            document
        )

        # 제목과 Section에도 키워드 검색 적용
        section = metadata.get("section", "")
        title = metadata.get("title", "")

        metadata_text = (
            f"{section} {title}"
        )

        k_score += keyword_score(
            query,
            metadata_text
        )

        # Hybrid 점수
        #
        # Vector 의미 검색을 기본으로 하면서
        # Keyword가 일치하면 추가 점수
        hybrid_score = (
            vector_score
            + (k_score * 0.15)
        )

        candidates.append({
            "text": document,
            "metadata": metadata,
            "distance": distance,
            "vector_score": vector_score,
            "keyword_score": k_score,
            "hybrid_score": hybrid_score
        })

    # Hybrid score가 높은 순서
    candidates.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )

    return candidates[:top_k]