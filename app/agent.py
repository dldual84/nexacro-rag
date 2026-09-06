import json
import re

import ollama

from tools.nexacro_search import NexacroSearchTool
from tools.nexacro_api_search import NexacroApiSearchTool
from tools.nexacro_example_search import NexacroExampleSearchTool

from app.llm import (
    generate_answer,
    generate_without_search
)


class NexacroAgent:

    def __init__(self):
        self.tools = {
            "nexacro_search": NexacroSearchTool(),
            "nexacro_api_search": NexacroApiSearchTool(),
            "nexacro_example_search": NexacroExampleSearchTool()
        }

    # ==========================================================
    # Tool 선택
    # ==========================================================

    def infer_tools(self, question):
        question_lower = question.lower()
        tools = []

        api_keywords = [
            "property",
            "속성",
            "method",
            "메서드",
            "함수",
            "event",
            "이벤트",
            "파라미터",
            "parameter",
            "반환값",
            "return",
            "set_",
            "get_",
            "truevalue",
            "falsevalue"
        ]

        if any(keyword in question_lower for keyword in api_keywords):
            tools.append("nexacro_api_search")

        example_keywords = [
            "예제",
            "샘플",
            "example",
            "sample",
            "구현",
            "만들기",
            "사용하기",
            "설정하기",
            "적용하기",
            "처리하기",
            "코드"
        ]

        if any(keyword in question_lower for keyword in example_keywords):
            tools.append("nexacro_example_search")

        if not tools:
            tools.append("nexacro_search")

        return tools

    # ==========================================================
    # Planner
    # ==========================================================

    def plan(self, question):
        prompt = f"""
너는 Nexacro 17 문서 검색 Agent의 Planner다.

사용자의 질문을 보고 필요한 검색 Tool을 선택한다.

사용 가능한 Tool:

1. nexacro_search
- 일반 Nexacro 기능
- Component 설명
- 기본 사용법
- 개념 설명

2. nexacro_api_search
- Property
- Method
- Event
- API
- 파라미터
- 반환값

3. nexacro_example_search
- 예제
- 샘플
- 실제 구현
- 코드
- Component 사용 예제

규칙:
- 필요한 Tool만 선택한다.
- 하나 이상 선택할 수 있다.
- 예제와 API를 함께 질문하면 둘 다 선택한다.
- 단순 기본 설명이면 nexacro_search를 우선한다.
- JSON 배열만 출력한다.

예:
["nexacro_api_search"]

또는:

["nexacro_api_search", "nexacro_example_search"]

질문:
{question}
"""

        try:
            response = ollama.chat(
                model="qwen3:8b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response["message"]["content"]

            match = re.search(
                r"\[[\s\S]*?\]",
                content
            )

            if match:
                tools = json.loads(match.group(0))

                valid_tools = [
                    tool
                    for tool in tools
                    if tool in self.tools
                ]

                if valid_tools:
                    return valid_tools

        except Exception as e:
            print("Planner ERROR:", repr(e))

        return self.infer_tools(question)

    # ==========================================================
    # Tool 실행
    # ==========================================================

    def execute_tool(self, tool_name, question):
        tool = self.tools.get(tool_name)

        if tool is None:
            return []

        try:
            return tool.run(question)

        except Exception as e:
            print(
                f"Tool ERROR [{tool_name}]:",
                repr(e)
            )
            return []

    # ==========================================================
    # 질문에서 API / Component / 핵심 키워드 추출
    # ==========================================================

    def extract_query_terms(self, question):
        """
        질문에서 검색 결과 선별에 사용할 핵심 용어를 추출한다.

        예:
        "Grid의 setCellProperty 메서드는 어떻게 사용하는가?"

        ->
        [
            "grid",
            "setcellproperty"
        ]
        """

        tokens = re.findall(
            r"[가-힣]+|[a-zA-Z_][a-zA-Z0-9_]*",
            question.lower()
        )

        stopwords = {
            "어떻게",
            "무엇",
            "뭔지",
            "뭔가",
            "알려줘",
            "설명",
            "설명해줘",
            "사용",
            "사용하는",
            "사용방법",
            "방법",
            "예제",
            "실제",
            "보여줘",
            "보여",
            "알려",
            "대한",
            "에서",
            "의",
            "가",
            "을",
            "를",
            "은",
            "는",
            "이",
            "그",
            "좀"
        }

        result = []

        for token in tokens:
            if len(token) < 2:
                continue

            if token in stopwords:
                continue

            if token not in result:
                result.append(token)

        return result

    # ==========================================================
    # API 이름 추출
    # ==========================================================

    def extract_api_names(self, question):
        """
        질문에 명시된 API 이름을 추출한다.

        예:
        setCellProperty
        getCellProperty
        addEventHandler
        truevalue
        falsevalue
        """

        patterns = [
            r"\bset[A-Za-z0-9_]+\b",
            r"\bget[A-Za-z0-9_]+\b",
            r"\badd[A-Za-z0-9_]+\b",
            r"\bremove[A-Za-z0-9_]+\b",
            r"\bon[A-Za-z0-9_]+\b",
            r"\b[a-zA-Z_][a-zA-Z0-9_]*\(",
        ]

        results = []

        for pattern in patterns:
            matches = re.findall(
                pattern,
                question
            )

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

    # ==========================================================
    # Component 추출
    # ==========================================================

    def detect_components(self, question):
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

        question_lower = question.lower()

        result = []

        for component in components:

            if component.lower() in question_lower:
                result.append(component.lower())

        return result

    # ==========================================================
    # 질문 유형
    # ==========================================================

    def detect_question_type(self, question):
        question_lower = question.lower()

        is_example = any(
            keyword in question_lower
            for keyword in [
                "예제",
                "샘플",
                "example",
                "sample",
                "코드",
                "구현",
                "사용하는 방법",
                "사용방법"
            ]
        )

        is_api = any(
            keyword in question_lower
            for keyword in [
                "property",
                "속성",
                "method",
                "메서드",
                "event",
                "이벤트",
                "함수",
                "truevalue",
                "falsevalue",
                "set_",
                "get_"
            ]
        )

        if is_example and is_api:
            return "API_EXAMPLE"

        if is_example:
            return "EXAMPLE"

        if is_api:
            return "API"

        return "GENERAL"

    # ==========================================================
    # 실제 코드 존재 여부
    # ==========================================================

    def has_real_code(self, text):
        """
        단순 API 설명이 아니라 실제 구현 코드가 있는지 판단한다.
        """

        if not text:
            return False

        code_patterns = [
            r"\bthis\.[A-Za-z_][A-Za-z0-9_]*\s*=",

            r"\bthis\.[A-Za-z_][A-Za-z0-9_]*\."
            r"[A-Za-z_][A-Za-z0-9_]*\s*\(",

            r"\bfunction\s+\w+",

            r"\bvar\s+\w+\s*=",

            r"\blet\s+\w+\s*=",

            r"\bconst\s+\w+\s*=",

            r"\bif\s*\(",

            r"\belse\s+if\s*\(",

            r"\bfor\s*\(",

            r"\bwhile\s*\(",

            r"\baddEventHandler\s*\(",

            r"\baddEventListener\s*\(",

            r"\bsetCellProperty\s*\(",

            r"\bgetCellProperty\s*\(",

            r"\bsetColumn\s*\(",

            r"\bgetColumn\s*\(",

            r"\bgetRow\s*\(",

            r"\baddRow\s*\(",

            r"\bdeleteRow\s*\(",

            r"\binsertRow\s*\(",

            r"===",

            r"!==",

            r"=>"
        ]

        for pattern in code_patterns:

            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                return True

        return False

    # ==========================================================
    # 문서가 질문의 API를 직접 포함하는지
    # ==========================================================

    def has_exact_api(self, question, document):
        """
        질문에 명시된 API가 문서에 직접 등장하는지 확인한다.

        예:
        질문:
            Grid의 setCellProperty 메서드는?

        문서:
            this.Grid00.setCellProperty(...)

        -> True
        """

        api_names = self.extract_api_names(question)

        if not api_names:
            return False

        metadata = document.get(
            "metadata",
            {}
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

        combined = (
            f"{title} "
            f"{section} "
            f"{text}"
        ).lower()

        for api_name in api_names:

            if api_name.lower() in combined:
                return True

        return False

    # ==========================================================
    # 문서 점수 계산
    # ==========================================================

    def calculate_document_score(
        self,
        question,
        document
    ):
        metadata = document.get(
            "metadata",
            {}
        )

        title = str(
            metadata.get("title", "")
        )

        section = str(
            metadata.get("section", "")
        )

        source = str(
            metadata.get("source", "")
        )

        text = str(
            document.get("text", "")
        )

        title_lower = title.lower()
        section_lower = section.lower()
        source_lower = source.lower()
        text_lower = text.lower()

        question_lower = question.lower()

        question_type = self.detect_question_type(
            question
        )

        query_terms = self.extract_query_terms(
            question
        )

        api_names = self.extract_api_names(
            question
        )

        components = self.detect_components(
            question
        )

        score = 0

        # ------------------------------------------------------
        # 기존 검색 점수
        # ------------------------------------------------------

        score += (
            document.get(
                "hybrid_score",
                0
            ) * 10
        )

        score += (
            document.get(
                "ranking_score",
                0
            ) * 5
        )

        score += (
            document.get(
                "api_score",
                0
            ) * 0.5
        )

        score += (
            document.get(
                "final_example_score",
                0
            ) * 0.5
        )

        # ------------------------------------------------------
        # 질문 핵심 단어
        # ------------------------------------------------------

        for term in query_terms:

            if term in title_lower:
                score += 12

            elif term in section_lower:
                score += 8

            elif term in text_lower:
                score += 3

        # ------------------------------------------------------
        # Component
        # ------------------------------------------------------

        for component in components:

            if component in title_lower:
                score += 25

            elif component in section_lower:
                score += 18

            elif component in text_lower:
                score += 5

        # ------------------------------------------------------
        # API 이름
        # ------------------------------------------------------

        for api_name in api_names:

            api_lower = api_name.lower()

            if api_lower in title_lower:
                score += 40

            elif api_lower in section_lower:
                score += 30

            elif api_lower in text_lower:
                score += 20

        # ------------------------------------------------------
        # Property 질문
        # ------------------------------------------------------

        if "property" in question_lower \
                or "속성" in question_lower:

            if "property" in title_lower:
                score += 25

            if "property" in section_lower:
                score += 20

        # ------------------------------------------------------
        # Method 질문
        # ------------------------------------------------------

        if "method" in question_lower \
                or "메서드" in question_lower:

            if "method" in title_lower:
                score += 25

            if "method" in section_lower:
                score += 20

        # ------------------------------------------------------
        # Event 질문
        # ------------------------------------------------------

        if "event" in question_lower \
                or "이벤트" in question_lower:

            if "event" in title_lower:
                score += 25

            if "event" in section_lower:
                score += 20

        # ------------------------------------------------------
        # 실제 코드
        # ------------------------------------------------------

        real_code = self.has_real_code(
            text
        )

        if real_code:

            if question_type in [
                "EXAMPLE",
                "API_EXAMPLE"
            ]:
                score += 35

        else:

            if question_type == "EXAMPLE":
                score -= 15

            if question_type == "API_EXAMPLE":
                score -= 10

        # ------------------------------------------------------
        # 정확한 API가 문서에 존재
        # ------------------------------------------------------

        if self.has_exact_api(
            question,
            document
        ):
            score += 45

        # ------------------------------------------------------
        # Workbook 예제 우선
        # ------------------------------------------------------

        if "nexacro_workbook" in source_lower:

            if question_type in [
                "EXAMPLE",
                "API_EXAMPLE"
            ]:
                score += 15

        # ------------------------------------------------------
        # Manual API 문서
        # ------------------------------------------------------

        if "nexacro_manual" in source_lower:

            if question_type == "EXAMPLE":

                # 단순 API 설명 문서는
                # 실제 예제 질문에서는 후순위
                if (
                    "property" in title_lower
                    or "method" in title_lower
                    or "event" in title_lower
                ):
                    score -= 20

        # ------------------------------------------------------
        # 질문에 특정 API가 있는데
        # 해당 API가 문서에 없는 경우 감점
        # ------------------------------------------------------

        if api_names:

            has_api = any(
                api_name.lower()
                in text_lower
                for api_name in api_names
            )

            if not has_api:
                score -= 25

        return score

    # ==========================================================
    # 문서 선별
    # ==========================================================

    def select_documents(
        self,
        question,
        documents,
        max_documents=8
    ):
        """
        검색 결과를 질문에 맞게 재정렬하고
        관련성이 낮은 문서를 제거한다.
        """

        if not documents:
            return []

        scored = []

        for document in documents:

            score = self.calculate_document_score(
                question,
                document
            )

            document["agent_score"] = score

            scored.append(document)

        scored.sort(
            key=lambda item: (
                item.get(
                    "agent_score",
                    0
                ),
                item.get(
                    "hybrid_score",
                    0
                )
            ),
            reverse=True
        )

        question_type = self.detect_question_type(
            question
        )

        api_names = self.extract_api_names(
            question
        )

        selected = []

        # ------------------------------------------------------
        # 특정 API 질문
        # ------------------------------------------------------

        if api_names:

            exact_documents = []

            for document in scored:

                if self.has_exact_api(
                    question,
                    document
                ):
                    exact_documents.append(
                        document
                    )

            if exact_documents:

                # 정확한 API가 발견된 경우
                # 상위 결과를 우선 사용한다.
                selected.extend(
                    exact_documents[:max_documents]
                )

        # ------------------------------------------------------
        # 일반적인 경우
        # ------------------------------------------------------

        if len(selected) < max_documents:

            for document in scored:

                if document in selected:
                    continue

                selected.append(
                    document
                )

                if len(selected) >= max_documents:
                    break

        # ------------------------------------------------------
        # 예제 질문에서 실제 코드가 있는 문서 우선
        # ------------------------------------------------------

        if question_type in [
            "EXAMPLE",
            "API_EXAMPLE"
        ]:

            code_documents = [
                document
                for document in selected
                if self.has_real_code(
                    document.get(
                        "text",
                        ""
                    )
                )
            ]

            non_code_documents = [
                document
                for document in selected
                if not self.has_real_code(
                    document.get(
                        "text",
                        ""
                    )
                )
            ]

            # 실제 코드가 존재하면
            # 코드 문서를 앞쪽에 배치한다.
            selected = (
                code_documents
                + non_code_documents
            )

        return selected[:max_documents]

    # ==========================================================
    # 문서 병합
    # ==========================================================

    def merge_documents(self, documents):

        merged = {}

        for document in documents:

            metadata = document.get(
                "metadata",
                {}
            )

            source = str(
                metadata.get(
                    "source",
                    ""
                )
            )

            section = str(
                metadata.get(
                    "section",
                    ""
                )
            )

            title = str(
                metadata.get(
                    "title",
                    ""
                )
            )

            text = str(
                document.get(
                    "text",
                    ""
                )
            )

            key = (
                source,
                section,
                title,
                text[:300]
            )

            if key not in merged:

                merged[key] = document

            else:

                old_score = merged[key].get(
                    "hybrid_score",
                    0
                )

                new_score = document.get(
                    "hybrid_score",
                    0
                )

                if new_score > old_score:
                    merged[key] = document

        return list(
            merged.values()
        )

    # ==========================================================
    # 문서 관련성 평가
    # ==========================================================

    def evaluate_documents(
        self,
        question,
        documents
    ):
        if not documents:
            return False

        question_lower = question.lower()

        tokens = re.findall(
            r"[가-힣]+|[a-zA-Z_][a-zA-Z0-9_]*|\d+",
            question_lower
        )

        if not tokens:
            return bool(documents)

        best_score = 0

        for document in documents:

            metadata = document.get(
                "metadata",
                {}
            )

            title = str(
                metadata.get(
                    "title",
                    ""
                )
            ).lower()

            section = str(
                metadata.get(
                    "section",
                    ""
                )
            ).lower()

            text = str(
                document.get(
                    "text",
                    ""
                )
            ).lower()

            combined = (
                f"{title} "
                f"{section} "
                f"{text}"
            )

            score = 0

            for token in tokens:

                if len(token) < 2:
                    continue

                if token in title:
                    score += 5

                elif token in section:
                    score += 3

                elif token in combined:
                    score += 1

            score += (
                document.get(
                    "hybrid_score",
                    0
                ) * 3
            )

            best_score = max(
                best_score,
                score
            )

        return best_score >= 3

    # ==========================================================
    # 추가 Tool 판단
    # ==========================================================

    def get_additional_tools(
        self,
        question,
        selected_tools
    ):
        inferred = self.infer_tools(
            question
        )

        return [
            tool
            for tool in inferred
            if tool not in selected_tools
        ]

    # ==========================================================
    # Agent 실행
    # ==========================================================

    def run(self, question):

        print("=" * 70)
        print("Nexacro Agent")
        print("=" * 70)

        print(
            "Question:",
            question
        )

        # ------------------------------------------------------
        # 질문 유형 출력
        # ------------------------------------------------------

        question_type = self.detect_question_type(
            question
        )

        print(
            "Question Type:",
            question_type
        )

        # ------------------------------------------------------
        # Planner
        # ------------------------------------------------------

        selected_tools = self.plan(
            question
        )

        print(
            "Planner:",
            selected_tools
        )

        # ------------------------------------------------------
        # Tool 실행
        # ------------------------------------------------------

        all_documents = []

        for tool_name in selected_tools:

            print(
                f"Tool 실행: {tool_name}"
            )

            documents = self.execute_tool(
                tool_name,
                question
            )

            print(
                f"검색 결과: {len(documents)}"
            )

            all_documents.extend(
                documents
            )

        # ------------------------------------------------------
        # 문서 병합
        # ------------------------------------------------------

        documents = self.merge_documents(
            all_documents
        )

        print(
            "병합 후:",
            len(documents)
        )

        # ------------------------------------------------------
        # 관련성 부족하면 추가 Tool
        # ------------------------------------------------------

        if not self.evaluate_documents(
            question,
            documents
        ):

            additional_tools = (
                self.get_additional_tools(
                    question,
                    selected_tools
                )
            )

            print(
                "추가 검색:",
                additional_tools
            )

            for tool_name in additional_tools:

                extra_documents = (
                    self.execute_tool(
                        tool_name,
                        question
                    )
                )

                documents.extend(
                    extra_documents
                )

            documents = self.merge_documents(
                documents
            )

        # ------------------------------------------------------
        # Agent 자체 문서 선별
        # ------------------------------------------------------

        documents = self.select_documents(
            question=question,
            documents=documents,
            max_documents=8
        )

        print(
            "최종 문서:",
            len(documents)
        )

        # ------------------------------------------------------
        # 디버깅용 문서 목록
        # ------------------------------------------------------

        print("-" * 70)
        print("최종 선택 문서")
        print("-" * 70)

        for index, document in enumerate(
            documents,
            start=1
        ):

            metadata = document.get(
                "metadata",
                {}
            )

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

            agent_score = document.get(
                "agent_score",
                0
            )

            hybrid_score = document.get(
                "hybrid_score",
                0
            )

            has_code = self.has_real_code(
                document.get(
                    "text",
                    ""
                )
            )

            print(
                f"[{index}] "
                f"score={agent_score:.2f} "
                f"hybrid={hybrid_score:.4f} "
                f"code={has_code}"
            )

            print(
                f"    source={source}"
            )

            print(
                f"    section={section}"
            )

            print(
                f"    title={title}"
            )

        print("-" * 70)

        # ------------------------------------------------------
        # 검색 결과 없음
        # ------------------------------------------------------

        if not documents:

            return generate_without_search(
                question
            )

        # ------------------------------------------------------
        # LLM
        # ------------------------------------------------------

        answer = generate_answer(
            question=question,
            contexts=documents
        )

        return answer