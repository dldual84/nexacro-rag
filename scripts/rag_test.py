from app.rag import RAG


def main():

    rag = RAG()

    print("=" * 70)
    print("Nexacro 17 RAG 테스트")
    print("=" * 70)

    while True:

        question = input("\n질문 (종료: q): ").strip()

        if question.lower() == "q":
            break

        if not question:
            continue

        print("\n검색 및 답변 생성 중...")

        result = rag.ask(
            question,
            top_k=5
        )

        print()
        print("=" * 70)
        print("답변")
        print("=" * 70)

        print(result["answer"])

        print()
        print("=" * 70)
        print("참고 문서")
        print("=" * 70)

        for index, source in enumerate(
            result["sources"],
            start=1
        ):

            metadata = source["metadata"]

            print(
                f"{index}. "
                f"{metadata.get('title', '')} "
                f"(p.{metadata.get('page', '')})"
            )


if __name__ == "__main__":
    main()