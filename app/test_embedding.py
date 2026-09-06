
import os

from dotenv import load_dotenv
from ollama import embed

load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL")


def main():
    response = embed(
        model=EMBED_MODEL,
        input="Nexacro 17 Grid에서 checkbox를 사용하는 방법"
    )

    embeddings = response.embeddings

    print("Embedding 생성 성공")
    print("벡터 개수:", len(embeddings))
    print("벡터 차원:", len(embeddings[0]))
    print("앞부분:", embeddings[0][:5])


if __name__ == "__main__":
    main()