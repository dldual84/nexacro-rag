from app.llm import generate_answer


def main():

    question = "Nexacro 17이 무엇인지 간단하게 설명해줘."

    context = """
Nexacro Platform은 애플리케이션을 개발하기 위한
개발 플랫폼입니다.
"""

    answer = generate_answer(
        question,
        context
    )

    print()
    print("=" * 70)
    print("답변")
    print("=" * 70)
    print(answer)


if __name__ == "__main__":
    main()