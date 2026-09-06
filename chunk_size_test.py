import json


CHUNK_PATH = "data/chunks.json"


def main():

    # --------------------------------------------------
    # Chunk 읽기
    # --------------------------------------------------

    with open(CHUNK_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print("=" * 70)
    print("Chunk Size Test")
    print("=" * 70)

    print(f"전체 Chunk 수 : {len(chunks)}")

    # --------------------------------------------------
    # 길이 계산
    # --------------------------------------------------

    sizes = []

    for chunk in chunks:

        text = chunk.get("text", "")

        sizes.append({
            "section": chunk.get("section", ""),
            "title": chunk.get("title", ""),
            "length": len(text)
        })

    # --------------------------------------------------
    # 통계
    # --------------------------------------------------

    lengths = [x["length"] for x in sizes]

    print()
    print("-" * 70)
    print("문자 수 통계")
    print("-" * 70)

    print(f"최소 : {min(lengths):,}")
    print(f"최대 : {max(lengths):,}")
    print(f"평균 : {sum(lengths) / len(lengths):,.1f}")

    # --------------------------------------------------
    # 구간별 개수
    # --------------------------------------------------

    ranges = [
        (0, 500),
        (501, 1000),
        (1001, 2000),
        (2001, 3000),
        (3001, 5000),
        (5001, 10000),
        (10001, float("inf"))
    ]

    print()
    print("-" * 70)
    print("Chunk 크기 분포")
    print("-" * 70)

    for min_size, max_size in ranges:

        count = sum(
            1
            for x in lengths
            if min_size <= x <= max_size
        )

        if max_size == float("inf"):
            label = f"{min_size:,} 이상"
        else:
            label = f"{min_size:,} ~ {max_size:,}"

        print(f"{label:20} : {count:,}")

    # --------------------------------------------------
    # 가장 긴 Chunk
    # --------------------------------------------------

    print()
    print("-" * 70)
    print("가장 긴 Chunk TOP 20")
    print("-" * 70)

    sizes.sort(
        key=lambda x: x["length"],
        reverse=True
    )

    for i, chunk in enumerate(sizes[:20], start=1):

        print(
            f"{i:2}. "
            f"{chunk['section']:10} "
            f"{chunk['length']:7,}자 "
            f"{chunk['title']}"
        )


if __name__ == "__main__":
    main()