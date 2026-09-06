from app.hybrid_search import HybridSearch


def main():

    print("=" * 70)
    print("Nexacro Hybrid Search Test")
    print("=" * 70)

    searcher = HybridSearch()

    while True:

        question = input(
            "\n질문 (종료: exit): "
        ).strip()

        if question.lower() == "exit":
            break

        print()
        print("검색 중...")

        results = searcher.search(
            query=question,
            top_k=5
        )

        print()
        print("=" * 70)
        print("Hybrid Search 결과")
        print("=" * 70)

        for i, result in enumerate(
            results,
            start=1
        ):

            metadata = result["metadata"]

            print()
            print(f"[{i}]")
            print(
                f"Section : "
                f"{metadata.get('section', '')}"
            )
            print(
                f"Title   : "
                f"{metadata.get('title', '')}"
            )
            print(
                f"Pages   : "
                f"{metadata.get('pages', '')}"
            )
            print(
                f"Distance: "
                f"{result['distance']}"
            )
            print(
                f"Vector Score : "
                f"{result['vector_score']:.4f}"
            )
            print(
                f"Keyword Score: "
                f"{result['keyword_score']:.4f}"
            )
            print(
                f"Hybrid Score : "
                f"{result['hybrid_score']:.4f}"
            )

            print("-" * 70)
            print(
                result["text"][:500]
            )


if __name__ == "__main__":
    main()