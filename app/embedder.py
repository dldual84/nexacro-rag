import ollama

EMBED_MODEL = "nomic-embed-text:latest"

# embedding에 넣을 최대 문자 수
# 너무 크게 잡지 않고 안정적으로 처리하기 위한 값
MAX_CHARS = 1500


def split_text(text, max_chars=MAX_CHARS):
    """
    긴 텍스트를 embedding 가능한 크기로 분할한다.
    문단/줄바꿈을 최대한 유지하면서 나눈다.
    """

    if not text:
        return []

    text = str(text).strip()

    if len(text) <= max_chars:
        return [text]

    chunks = []

    current = ""

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # 현재 chunk에 추가했을 때 너무 길어지는 경우
        if len(current) + len(line) + 1 > max_chars:

            if current:
                chunks.append(current)

            # 한 줄 자체가 너무 긴 경우
            if len(line) > max_chars:

                for i in range(0, len(line), max_chars):
                    chunks.append(line[i:i + max_chars])

                current = ""

            else:
                current = line

        else:

            if current:
                current += "\n"

            current += line

    if current:
        chunks.append(current)

    return chunks


def embed_text(text):
    """
    하나의 텍스트를 embedding한다.
    """

    response = ollama.embed(
        model=EMBED_MODEL,
        input=text
    )

    return response["embeddings"][0]


def embed_chunks(chunks):
    """
    chunk 목록을 embedding한다.

    긴 Section은 embedding용으로 여러 개로 분할한다.
    원래 Section 정보는 metadata에 유지한다.
    """

    results = []

    for index, chunk in enumerate(chunks):

        text = chunk["text"]

        split_chunks = split_text(text)

        for sub_index, sub_text in enumerate(split_chunks):

            embedding = embed_text(sub_text)

            result = {
                "id": f"{chunk['section']}_{sub_index}",
                "text": sub_text,
                "embedding": embedding,
                "metadata": {
                    "section": chunk["section"],
                    "title": chunk["title"],
                    "pages": ",".join(
                        map(str, chunk["pages"])
                    ),
                    "chunk_index": index,
                    "sub_chunk_index": sub_index
                }
            }

            results.append(result)

            print(
                f"[Embedding] "
                f"{index + 1}/{len(chunks)} "
                f"Section={chunk['section']} "
                f"Sub={sub_index + 1}/{len(split_chunks)}"
            )

    return results