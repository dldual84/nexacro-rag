import re

from app.hybrid_search import HybridSearch
from app.ranking import rank_documents


class NexacroApiSearchTool:

    name = "nexacro_api_search"

    description = """
    Nexacro 17 API 관련 문서를 검색한다.

    다음 질문에 사용:
    - Component Property
    - Property 값
    - Property 타입
    - Property 설정 방법
    - API Method
    - Method 사용 방법
    - Method 파라미터
    - Method 반환값
    - Event
    - Event 처리 방법
    """

    def __init__(self):
        self.searcher = HybridSearch()

    # ---------------------------------------------------------
    # 질문 의도 판별
    # ---------------------------------------------------------
    def detect_intent(self, query):

        query_lower = query.lower()

        method_keywords = [
            "메서드",
            "method",
            "함수",
            "호출",
            "호출방법",
            "사용방법",
            "파라미터",
            "parameter",
            "인자",
            "argument",
            "반환",
            "return",
            "리턴",
            "set_",
            "get_"
        ]

        property_keywords = [
            "속성",
            "property",
            "프로퍼티",
            "값",
            "value",
            "설정값",
            "기본값",
            "default",
            "truevalue",
            "falsevalue",
            "displaytype",
            "cellproperty"
        ]

        event_keywords = [
            "이벤트",
            "event",
            "onclick",
            "onitemchanged",
            "onchanged",
            "oncellclick",
            "onheadclick",
            "ondblclick"
        ]

        if any(keyword in query_lower for keyword in method_keywords):
            return "METHOD"

        if any(keyword in query_lower for keyword in property_keywords):
            return "PROPERTY"

        if any(keyword in query_lower for keyword in event_keywords):
            return "EVENT"

        return "API_GENERAL"

    # ---------------------------------------------------------
    # Component 추출
    # ---------------------------------------------------------
    def detect_components(self, query):

        components = [
            "Grid",
            "CheckBox",
            "Combo",
            "ComboBox",
            "Button",
            "Edit",
            "MaskEdit",
            "TextArea",
            "ListBox",
            "Radio",
            "Calendar",
            "Dataset",
            "Div",
            "Tab",
            "Form",
            "PopupDiv",
            "Static",
            "ImageViewer"
        ]

        query_lower = query.lower()

        result = []

        for component in components:
            if component.lower() in query_lower:
                result.append(component.lower())

        return result

    # ---------------------------------------------------------
    # Method 이름 추출
    # ---------------------------------------------------------
    def extract_method_names(self, query):

        patterns = [
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\(",
            r"\b(set_[a-zA-Z0-9_]+)",
            r"\b(get_[a-zA-Z0-9_]+)",
            r"\b(add[a-zA-Z0-9_]+)",
            r"\b(remove[a-zA-Z0-9_]+)"
        ]

        result = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                query
            )

            for match in matches:

                if isinstance(match, tuple):
                    match = match[0]

                match = match.rstrip("(")

                if match not in result:
                    result.append(match)

        return result

    # ---------------------------------------------------------
    # API 관련 문서인지 판단
    # ---------------------------------------------------------
    def is_api_document(self, document, intent):

        metadata = document.get("metadata", {})

        title = str(metadata.get("title", ""))
        section = str(metadata.get("section", ""))
        text = str(document.get("text", ""))
        source = str(metadata.get("source", ""))

        combined = (
            f"{title} "
            f"{section} "
            f"{text} "
            f"{source}"
        )

        combined_lower = combined.lower()

        score = 0

        # -----------------------------------------------------
        # 기본 API 키워드
        # -----------------------------------------------------

        api_keywords = [
            "property",
            "method",
            "event",
            "set_",
            "get_",
            "onclick",
            "onitemchanged",
            "oncellclick",
            "addEventHandler",
            "addEventListener"
        ]

        for keyword in api_keywords:

            if keyword.lower() in combined_lower:
                score += 1

        # -----------------------------------------------------
        # Intent별 가중치
        # -----------------------------------------------------

        if intent == "METHOD":

            method_keywords = [
                "method",
                "set_",
                "get_",
                "parameter",
                "argument",
                "return",
                "호출",
                "파라미터"
            ]

            for keyword in method_keywords:

                if keyword.lower() in combined_lower:
                    score += 4

        elif intent == "PROPERTY":

            property_keywords = [
                "property",
                "속성",
                "value",
                "기본값",
                "default"
            ]

            for keyword in property_keywords:

                if keyword.lower() in combined_lower:
                    score += 4

        elif intent == "EVENT":

            event_keywords = [
                "event",
                "이벤트",
                "onclick",
                "onitemchanged",
                "oncellclick",
                "addEventHandler"
            ]

            for keyword in event_keywords:

                if keyword.lower() in combined_lower:
                    score += 4

        else:

            score += 1

        return score

    # ---------------------------------------------------------
    # 최종 검색
    # ---------------------------------------------------------
    def run(
        self,
        query,
        search_top_k=50,
        ranking_top_k=5
    ):

        intent = self.detect_intent(query)

        components = self.detect_components(query)

        method_names = self.extract_method_names(query)

        documents = self.searcher.search(
            query=query,
            top_k=search_top_k
        )

        if not documents:
            return []

        scored_documents = []

        for document in documents:

            metadata = document.get("metadata", {})

            title = str(
                metadata.get("title", "")
            )

            section = str(
                metadata.get("section", "")
            )

            text = str(
                document.get("text", "")
            )

            source = str(
                metadata.get("source", "")
            )

            combined = (
                f"{title} "
                f"{section} "
                f"{text} "
                f"{source}"
            )

            combined_lower = combined.lower()

            score = 0

            # -------------------------------------------------
            # API 문서 여부
            # -------------------------------------------------

            score += self.is_api_document(
                document,
                intent
            )

            # -------------------------------------------------
            # Component 정확도
            # -------------------------------------------------

            for component in components:

                if component in title.lower():
                    score += 20

                elif component in section.lower():
                    score += 12

                elif component in combined_lower:
                    score += 5

            # -------------------------------------------------
            # Method 정확도
            # -------------------------------------------------

            for method_name in method_names:

                if method_name.lower() in title.lower():
                    score += 30

                elif method_name.lower() in combined_lower:
                    score += 15

            # -------------------------------------------------
            # Intent별 title 우선
            # -------------------------------------------------

            title_lower = title.lower()

            if intent == "METHOD":

                if "method" in title_lower:
                    score += 20

            elif intent == "PROPERTY":

                if "property" in title_lower:
                    score += 20

            elif intent == "EVENT":

                if "event" in title_lower:
                    score += 20

            # -------------------------------------------------
            # Workbook 우선
            # -------------------------------------------------

            if "nexacro_workbook" in source.lower():
                score += 5

            # -------------------------------------------------
            # Hybrid score
            # -------------------------------------------------

            hybrid_score = document.get(
                "hybrid_score",
                0
            )

            final_score = (
                score
                + hybrid_score * 8
            )

            scored_documents.append(
                {
                    "score": final_score,
                    "api_score": score,
                    "intent": intent,
                    "document": document
                }
            )

        scored_documents.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        results = []

        for item in scored_documents:

            document = item["document"]

            document["api_score"] = item["api_score"]
            document["api_intent"] = item["intent"]

            results.append(document)

            if len(results) >= ranking_top_k:
                break

        return results