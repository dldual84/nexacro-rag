from app.hybrid_search import HybridSearch
from app.ranking import rank_documents


class NexacroSearchTool:

    name = "nexacro_search"

    description = """
    Nexacro 17 개발 문서에서 일반적인 정보를 검색한다.

    다음 질문에 사용:
    - Nexacro 기능 설명
    - Component 기본 사용법
    - 화면 구성 방법
    - Dataset/Grid/Component 개념
    - 특정 기능의 일반적인 설명
    - API가 아닌 개념적인 질문
    """

    def __init__(self):
        self.searcher = HybridSearch()

    def run(self, query, search_top_k=30, ranking_top_k=8):

        documents = self.searcher.search(
            query=query,
            top_k=search_top_k
        )

        if not documents:
            return []

        ranked_documents = rank_documents(
            query=query,
            documents=documents,
            top_k=ranking_top_k
        )

        return ranked_documents