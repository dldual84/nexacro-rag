from tools.nexacro_example_search import (
    NexacroExampleSearchTool
)


def main():

    tool = NexacroExampleSearchTool()

    questions = [
        "CheckBox를 사용하는 예제를 보여줘",
        "CheckBox의 truevalue를 변경하는 예제를 보여줘",
        "Grid 데이터를 처리하는 예제를 보여줘",
        "Grid의 setCellProperty 메서드를 사용하는 예제를 보여줘"
    ]

    for question in questions:

        print()
        print("=" * 80)
        print("질문:", question)
        print("=" * 80)

        results = tool.run(
            question,
            search_top_k=50,
            ranking_top_k=5
        )

        for index, result in enumerate(
            results,
            start=1
        ):

            metadata = result.get(
                "metadata",
                {}
            )

            print()
            print(
                f"[{index}]"
            )

            print(
                "source:",
                metadata.get(
                    "source",
                    ""
                )
            )

            print(
                "section:",
                metadata.get(
                    "section",
                    ""
                )
            )

            print(
                "title:",
                metadata.get(
                    "title",
                    ""
                )
            )

            print(
                "example_score:",
                result.get(
                    "example_score"
                )
            )

            print(
                "hybrid_score:",
                result.get(
                    "hybrid_score"
                )
            )

            text = result.get(
                "text",
                ""
            )

            print(
                "code:",
                "YES"
                if result.get("has_code")
                else "NO"
            )

            if result.get("has_code"):
                print("text preview:")
                print(text[:500])


if __name__ == "__main__":
    main()