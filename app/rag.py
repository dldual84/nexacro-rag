from app.hybrid_search import HybridSearch
from app.ranking import rank_documents
from app.llm import generate_answer


def ask(
    question,
    search_top_k=20,
    ranking_top_k=5
):

    # ==================================================
    # 1. Hybrid Search
    # ==================================================

    searcher = HybridSearch()

    documents = searcher.search(
        query=question,
        top_k=search_top_k
    )

    # ==================================================
    # 2. Ranking
    # ==================================================

    ranked_documents = rank_documents(
        query=question,
        documents=documents,
        top_k=ranking_top_k
    )

    # ==================================================
    # 3. LLM 답변 생성
    # ==================================================

    answer = generate_answer(
        question=question,
        contexts=ranked_documents
    )

    return {
        "question": question,
        "answer": answer,
        "contexts": ranked_documents
    }


# ======================================================
# RAG 테스트
# ======================================================

if __name__ == "__main__":

    query = "CheckBox의 truevalue 속성은 무엇인가?"

    print("=" * 70)
    print("Nexacro 17 RAG Test")
    print("=" * 70)

    print()
    print(f"질문: {query}")

    print()
    print("Hybrid Search + Ranking + LLM 실행 중...")
    print()

    result = ask(
        question=query,
        search_top_k=20,
        ranking_top_k=5
    )

    print("=" * 70)
    print("[답변]")
    print("=" * 70)

    print(result["answer"])

    print()
    print("=" * 70)
    print("[참고 문서]")
    print("=" * 70)

    for i, document in enumerate(
        result["contexts"],
        start=1
    ):

        metadata = document.get(
            "metadata",
            {}
        )

        print()
        print(
            f"{i}. "
            f"{metadata.get('source', '')} / "
            f"{metadata.get('section', '')} / "
            f"{metadata.get('title', '')}"
        )

        print(
            f"   Ranking Score: "
            f"{document.get('ranking_score', 0):.4f}"
        )