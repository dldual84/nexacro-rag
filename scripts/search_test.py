from app.retriever import Retriever


def main():
    print("검색 테스트 시작")

    question = input("질문: ")

    print("검색 중...")

    retriever = Retriever()

    results = retriever.search(
        question,
        top_k=5
    )

    print()
    print("=" * 70)
    print("검색 결과")
    print("=" * 70)

    for index, result in enumerate(results, start=1):

        metadata = result["metadata"]

        print()
        print(f"[{index}]")
        print("거리:", result["distance"])
        print("Section:", metadata.get("section"))
        print("Title:", metadata.get("title"))
        print("Page:", metadata.get("page"))

        print()
        print(result["text"][:1000])


if __name__ == "__main__":
    main()