from tools.nexacro_api_search import (
    NexacroApiSearchTool
)


def main():

    tool = NexacroApiSearchTool()

    questions = [
        "CheckBox의 truevalue는 무엇인가?",
        "Grid의 setCellProperty 메서드는 어떻게 사용하는가?",
        "Button click 이벤트는 어떻게 처리하는가?",
        "Grid의 displaytype Property는 무엇인가?"
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
                "api_score:",
                result.get(
                    "api_score"
                )
            )

            print(
                "hybrid_score:",
                result.get(
                    "hybrid_score"
                )
            )


if __name__ == "__main__":
    main()