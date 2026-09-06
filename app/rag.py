from app.hybrid_search import HybridSearch
from app.ranking import rank_documents
from app.llm import generate_answer


def ask(
    question,
    search_top_k=30,
    ranking_top_k=8
):

    searcher = HybridSearch()

    documents = searcher.search(
        query=question,
        top_k=search_top_k
    )

    ranked_documents = rank_documents(
        query=question,
        documents=documents,
        top_k=ranking_top_k
    )

    answer = generate_answer(
        question=question,
        contexts=ranked_documents
    )

    return {
        "question": question,
        "answer": answer,
        "contexts": ranked_documents
    }