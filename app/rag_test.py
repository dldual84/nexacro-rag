from app.rag import ask


def print_separator():

    print("=" * 70)


def main():

    print_separator()
    print("Nexacro Ranking RAG Test")
    print_separator()

    while True:

        question = input(
            "\n질문 (종료: exit): "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        print()
        print("검색 + Ranking 중...")
        print()

        result = ask(
            question=question,
            top_k=3
        )

        contexts = result["contexts"]

        # --------------------------------------------------
        # Ranking 결과
        # --------------------------------------------------

        print_separator()
        print("Ranking 결과")
        print_separator()

        for i, context in enumerate(
            contexts,
            start=1
        ):

            metadata = context.get(
                "metadata",
                {}
            )

            print()
            print(f"[{i}]")

            print(
                "Section :",
                metadata.get(
                    "section",
                    ""
                )
            )

            print(
                "Title   :",
                metadata.get(
                    "title",
                    ""
                )
            )

            print(
                "Pages   :",
                metadata.get(
                    "pages",
                    ""
                )
            )

            print(
                "Distance:",
                context.get(
                    "distance"
                )
            )

            print(
                "Vector Score :",
                f"{context.get('vector_score', 0):.4f}"
            )

            print(
                "Keyword Score:",
                f"{context.get('keyword_score', 0):.4f}"
            )

            print(
                "Hybrid Score :",
                f"{context.get('hybrid_score', 0):.4f}"
            )

            print(
                "Ranking Score:",
                f"{context.get('ranking_score', 0):.4f}"
            )

            print("-" * 70)

            print(
                context.get(
                    "text",
                    ""
                )
            )

        # --------------------------------------------------
        # LLM 답변
        # --------------------------------------------------

        print()
        print_separator()
        print("답변")
        print_separator()
        print()

        print(
            result["answer"]
        )

        # --------------------------------------------------
        # 시간
        # --------------------------------------------------

        print()
        print_separator()

        print(
            f"검색 + Ranking 시간 : "
            f"{result['search_time']:.2f}초"
        )

        print(
            f"LLM 시간            : "
            f"{result['llm_time']:.2f}초"
        )

        print(
            f"전체 시간           : "
            f"{result['total_time']:.2f}초"
        )

        print_separator()


if __name__ == "__main__":
    main()