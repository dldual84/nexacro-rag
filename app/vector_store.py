import chromadb

from ollama import embed


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "nexacro_17"

EMBED_MODEL = "nomic-embed-text:latest"

# 한 번에 embedding할 문서 수
EMBED_BATCH_SIZE = 32


class VectorStore:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    def add_documents(self, documents):
        """
        documents:
        [
            {
                "id": "...",
                "text": "...",
                "metadata": {...}
            }
        ]
        """

        total = len(documents)

        for start in range(0, total, EMBED_BATCH_SIZE):

            batch = documents[
                start:start + EMBED_BATCH_SIZE
            ]

            ids = []
            texts = []
            metadatas = []

            for document in batch:
                ids.append(document["id"])
                texts.append(document["text"])
                metadatas.append(document["metadata"])

            print(
                f"Embedding "
                f"{start + 1} ~ {start + len(batch)} "
                f"/ {total}"
            )

            response = embed(
                model=EMBED_MODEL,
                input=texts
            )

            embeddings = response.embeddings

            self.collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )

    def search(self, query, top_k=5):
        """
        사용자 질문과 가장 유사한 문서를 검색한다.
        """

        response = embed(
            model=EMBED_MODEL,
            input=query
        )

        query_embedding = response.embeddings[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results

    def count(self):
        return self.collection.count()

    def get_all_documents(self):

        results = self.collection.get(
            include=[
                "documents",
                "metadatas"
            ]
        )

        documents = []

        texts = results.get(
            "documents",
            []
        )

        metadatas = results.get(
            "metadatas",
            []
        )

        for i, text in enumerate(texts):

            metadata = (
                metadatas[i]
                if i < len(metadatas)
                else {}
            )

            documents.append({
                "text": text,
                "metadata": metadata
            })

        return documents