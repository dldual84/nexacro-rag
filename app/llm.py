from dotenv import load_dotenv

import ollama
import os


load_dotenv()

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "qwen3:8b"
)


def generate_answer(
    question,
    contexts
):

    context_text = []

    for i, context in enumerate(
        contexts,
        start=1
    ):

        metadata = context.get(
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

        pages = metadata.get(
            "pages",
            ""
        )

        path = metadata.get(
            "path",
            ""
        )

        ranking_score = context.get(
            "ranking_score",
            0.0
        )

        text = context.get(
            "text",
            ""
        )

        context_text.append(
            f"""
[문서 {i}]
Source: {source}
Section: {section}
Title: {title}
Pages: {pages}
Path: {path}
Ranking Score: {ranking_score:.4f}

{text}
"""
        )

    context = "\n".join(
        context_text
    )

    prompt = f"""
너는 Nexacro 17 개발 문서를 기반으로 답변하는
기술 문서 도우미다.

아래 제공된 문서 내용만 근거로 질문에 답변하라.

답변 규칙:

1. 제공된 문서에 있는 내용을 우선적으로 사용한다.
2. 문서에 없는 내용은 사실인 것처럼 추측하지 않는다.
3. 질문과 직접 관련된 내용을 먼저 설명한다.
4. Nexacro 속성이나 API 이름은 원래 이름을 유지한다.
5. 필요한 경우 Nexacro JavaScript 코드 예제를 보여준다.
6. 답변 마지막에 참고한 Source / Section / Title을 표시한다.
7. 제공된 문서에서 질문에 대한 근거를 찾을 수 없다면
   "제공된 문서에서 확인할 수 없습니다."라고 답한다.
8. 일반적인 JavaScript 지식을 이용하여 문서에 없는 Nexacro 기능을
   임의로 만들어내지 않는다.

[질문]

{question}

[참고 문서]

{context}
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response[
        "message"
    ][
        "content"
    ]