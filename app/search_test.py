from app.vector_store import VectorStore
from app.search import search


def main():

    print("=" * 70)
    print("Nexacro RAG Search Test")
    print("=" * 70)

    store = VectorStore()

    print(f"ChromaDB 문서 수: {store.count()}")

    print()
    print("=" * 70)

    query = input("질문을 입력하세요: ")

    print("=" * 70)
    print(f"질문: {query}")
    print("=" * 70)

    results = search(
        query=query,
        top_k=8,
        max_results=5
    )

    for i, result in enumerate(results, start=1):

        print()
        print("-" * 70)
        print(f"[{i}]")
        print(f"Section : {result['metadata'].get('section')}")
        print(f"Title   : {result['metadata'].get('title')}")
        print(f"Pages   : {result['metadata'].get('pages')}")
        print(f"Distance: {result['distance']}")
        print("-" * 70)

        print(result["text"][:1000])


if __name__ == "__main__":
    main()