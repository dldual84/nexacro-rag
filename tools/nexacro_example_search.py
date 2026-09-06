import re

from app.hybrid_search import HybridSearch


class NexacroExampleSearchTool:

    name = "nexacro_example_search"

    description = """
    Nexacro 17 실제 사용 예제와 샘플을 검색한다.

    다음 질문에 사용:
    - 예제 코드
    - 샘플 코드
    - 실제 구현 방법
    - 특정 기능 구현 예제
    - API 사용 예제
    - Property 설정 예제
    - Event 처리 예제
    - Component 사용 예제
    """

    def __init__(self):
        self.searcher = HybridSearch()

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
            "ImageViewer",
            "FileUpload",
            "FileDownload",
            "WebBrowser",
            "WebView",
            "Tree",
            "ListView"
        ]

        query_lower = query.lower()

        result = []

        for component in components:
            if component.lower() in query_lower:
                result.append(component.lower())

        return result

    # ---------------------------------------------------------
    # API / Property / Event 이름 추출
    # ---------------------------------------------------------
    def extract_api_names(self, query):
        patterns = [
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\(",
            r"\bset_[a-zA-Z0-9_]+",
            r"\bget_[a-zA-Z0-9_]+",
            r"\badd[a-zA-Z0-9_]+",
            r"\bremove[a-zA-Z0-9_]+",
            r"\bon[a-zA-Z0-9_]+"
        ]

        results = []

        for pattern in patterns:
            matches = re.findall(pattern, query)

            for match in matches:

                if isinstance(match, tuple):
                    match = match[0]

                match = match.rstrip("(")

                if len(match) < 3:
                    continue

                if match.lower() not in [
                    item.lower()
                    for item in results
                ]:
                    results.append(match)

        return results

    # ---------------------------------------------------------
    # Property / API 키워드
    # ---------------------------------------------------------
    def detect_function_keywords(self, query):

        keywords = [
            # Dataset
            "dataset",
            "getcolumn",
            "setcolumn",
            "getrow",
            "setrow",
            "addrow",
            "insertrow",
            "deleterow",
            "delete",
            "filter",
            "sort",
            "keystring",
            "rowposition",

            # Grid
            "cell",
            "cellproperty",
            "setcellproperty",
            "getcellproperty",
            "displaytype",
            "edittype",
            "expr",
            "suppress",

            # CheckBox
            "truevalue",
            "falsevalue",
            "value",
            "checked",

            # Event
            "event",
            "onclick",
            "onitemchanged",
            "oncellclick",
            "onheadclick",
            "ondblclick",
            "addEventHandler",

            # 일반 구현 키워드
            "binding",
            "바인딩",
            "데이터",
            "처리",
            "변경",
            "조회",
            "삭제",
            "추가",
            "설정",
            "연결",
            "구현",
            "사용"
        ]

        query_lower = query.lower()

        result = []

        for keyword in keywords:
            if keyword.lower() in query_lower:
                result.append(keyword.lower())

        return result

    # ---------------------------------------------------------
    # 질문이 실제 "예제"를 요구하는지 판단
    # ---------------------------------------------------------
    def is_example_question(self, query):

        example_keywords = [
            "예제",
            "샘플",
            "example",
            "sample",
            "코드",
            "구현",
            "사용하기",
            "사용하는",
            "사용 방법",
            "사용방법",
            "만들기",
            "만드는",
            "설정하기",
            "설정하는",
            "적용하기",
            "적용하는",
            "처리하기",
            "처리하는"
        ]

        query_lower = query.lower()

        return any(
            keyword.lower() in query_lower
            for keyword in example_keywords
        )

    # ---------------------------------------------------------
    # 실제 코드인지 판단
    #
    # 단순 API Syntax:
    #   Grid.setCellProperty(...)
    #
    # 보다 실제 구현 코드:
    #   this.Grid00.setCellProperty(...)
    #
    # 를 높게 평가한다.
    # ---------------------------------------------------------
    def has_real_example_code(self, text):

        if not text:
            return False

        real_code_patterns = [

            # Nexacro 실제 Form Script
            r"\bthis\.[A-Za-z_][A-Za-z0-9_]*\s*=",

            # this.Grid00.xxx()
            r"\bthis\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\s*\(",

            # function
            r"\bfunction\s+\w+",

            # 변수 선언 및 대입
            r"\bvar\s+\w+\s*=",
            r"\blet\s+\w+\s*=",
            r"\bconst\s+\w+\s*=",

            # 조건문
            r"\bif\s*\(",
            r"\belse\s+if\s*\(",

            # 반복문
            r"\bfor\s*\(",
            r"\bwhile\s*\(",

            # Nexacro Event Handler
            r"\baddEventHandler\s*\(",
            r"\baddEventListener\s*\(",

            # 주요 Nexacro API
            r"\bsetCellProperty\s*\(",
            r"\bgetCellProperty\s*\(",
            r"\bsetColumn\s*\(",
            r"\bgetColumn\s*\(",
            r"\bgetRow\s*\(",
            r"\baddRow\s*\(",
            r"\bdeleteRow\s*\(",
            r"\binsertRow\s*\(",

            # JavaScript 비교 / 연산
            r"===",
            r"!==",
            r"=>"
        ]

        for pattern in real_code_patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True

        return False

    # ---------------------------------------------------------
    # API Syntax만 있는 문서인지 판단
    # ---------------------------------------------------------
    def has_api_syntax_only(self, text):

        if not text:
            return False

        syntax_patterns = [
            r"\b[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\s*\(",
            r"\b[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\s*"
        ]

        has_syntax = any(
            re.search(pattern, text)
            for pattern in syntax_patterns
        )

        if not has_syntax:
            return False

        return not self.has_real_example_code(text)

    # ---------------------------------------------------------
    # 문서가 API 문서인지 판단
    # ---------------------------------------------------------
    def is_manual_api_document(self, metadata):

        source = str(
            metadata.get("source", "")
        ).lower()

        title = str(
            metadata.get("title", "")
        ).lower()

        section = str(
            metadata.get("section", "")
        ).lower()

        combined = f"{title} {section}"

        if "nexacro_manual" not in source:
            return False

        api_keywords = [
            "_property_",
            "_method_",
            "_event_",
            " property",
            " method",
            " event",
            "property",
            "method",
            "event"
        ]

        return any(
            keyword in combined
            for keyword in api_keywords
        )

    # ---------------------------------------------------------
    # Example 점수 계산
    # ---------------------------------------------------------
    def example_score(self, document, query):

        metadata = document.get(
            "metadata",
            {}
        )

        source = str(
            metadata.get("source", "")
        )

        title = str(
            metadata.get("title", "")
        )

        section = str(
            metadata.get("section", "")
        )

        text = str(
            document.get("text", "")
        )

        source_lower = source.lower()
        title_lower = title.lower()
        section_lower = section.lower()
        text_lower = text.lower()

        score = 0

        # -----------------------------------------------------
        # 1. 실제 Workbook이면 기본 가산점
        # -----------------------------------------------------
        if "nexacro_workbook" in source_lower:
            score += 15

        # -----------------------------------------------------
        # 2. Manual API 문서는 일반 Example 검색에서 감점
        # -----------------------------------------------------
        if self.is_manual_api_document(metadata):
            score -= 20

        # -----------------------------------------------------
        # 3. 예제 제목 / Section
        # -----------------------------------------------------
        example_title_keywords = [
            "예제",
            "사용예",
            "사용 예",
            "예제구현",
            "예제구현방법",
            "예제에서사용한핵심기능",
            "example",
            "sample"
        ]

        for keyword in example_title_keywords:

            keyword_lower = keyword.lower()

            if keyword_lower in title_lower:
                score += 20

            if keyword_lower in section_lower:
                score += 10

        # -----------------------------------------------------
        # 4. 구현 관련 제목
        # -----------------------------------------------------
        implementation_keywords = [
            "구현",
            "사용",
            "설정",
            "적용",
            "처리",
            "변경",
            "생성",
            "만들기",
            "연결",
            "바인딩"
        ]

        for keyword in implementation_keywords:

            keyword_lower = keyword.lower()

            if keyword_lower in title_lower:
                score += 5

            elif keyword_lower in section_lower:
                score += 3

        # -----------------------------------------------------
        # 5. Component 매칭
        # -----------------------------------------------------
        components = self.detect_components(query)

        component_hit = False

        for component in components:

            if component in title_lower:
                score += 30
                component_hit = True

            elif component in section_lower:
                score += 20
                component_hit = True

            elif component in text_lower:
                score += 5
                component_hit = True

        # 질문에서 Component가 명확한데
        # 문서에 해당 Component가 전혀 없으면 강한 감점
        if components and not component_hit:
            score -= 30

        # -----------------------------------------------------
        # 6. API / Property / Event 이름 매칭
        # -----------------------------------------------------
        api_names = self.extract_api_names(query)

        for api_name in api_names:

            api_lower = api_name.lower()

            if api_lower in title_lower:
                score += 50

            elif api_lower in section_lower:
                score += 35

            elif api_lower in text_lower:
                score += 20

        # -----------------------------------------------------
        # 7. 질문에 포함된 기능 키워드
        # -----------------------------------------------------
        function_keywords = self.detect_function_keywords(
            query
        )

        for keyword in function_keywords:

            if keyword in title_lower:
                score += 15

            elif keyword in section_lower:
                score += 8

            elif keyword in text_lower:
                score += 3

        # -----------------------------------------------------
        # 8. 실제 예제 코드
        # -----------------------------------------------------
        real_code = self.has_real_example_code(
            text
        )

        if real_code:

            # Workbook의 실제 코드라면 강하게 가산
            if "nexacro_workbook" in source_lower:
                score += 30
            else:
                score += 10

        # -----------------------------------------------------
        # 9. API Syntax만 있는 문서는 실제 예제보다 낮게
        # -----------------------------------------------------
        if self.has_api_syntax_only(text):
            score -= 10

        # -----------------------------------------------------
        # 10. Hybrid Search 점수
        # -----------------------------------------------------
        hybrid_score = document.get(
            "hybrid_score",
            0
        )

        score += hybrid_score * 5

        return score

    # ---------------------------------------------------------
    # 검색
    # ---------------------------------------------------------
    def run(
        self,
        query,
        search_top_k=50,
        ranking_top_k=5
    ):

        documents = self.searcher.search(
            query=query,
            top_k=search_top_k
        )

        if not documents:
            return []

        scored_documents = []

        for document in documents:

            score = self.example_score(
                document,
                query
            )

            scored_documents.append({
                "score": score,
                "example_score": score,
                "document": document
            })

        # -----------------------------------------------------
        # 최종 정렬
        # -----------------------------------------------------
        scored_documents.sort(
            key=lambda item: (
                item["score"],
                item["document"].get(
                    "hybrid_score",
                    0
                )
            ),
            reverse=True
        )

        # -----------------------------------------------------
        # 결과 생성
        # -----------------------------------------------------
        results = []

        for item in scored_documents:

            document = item["document"]

            text = document.get(
                "text",
                ""
            )

            document["example_score"] = (
                item["example_score"]
            )

            document["final_example_score"] = (
                item["score"]
            )

            document["has_code"] = (
                self.has_real_example_code(text)
            )

            document["api_syntax_only"] = (
                self.has_api_syntax_only(text)
            )

            results.append(document)

            if len(results) >= ranking_top_k:
                break

        return results