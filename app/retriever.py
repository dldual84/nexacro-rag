import os

import chromadb

from dotenv import load_dotenv
from ollama import embed


load_dotenv()

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "nexacro_17"
EMBED_MODEL = os.getenv("EMBED_MODEL")


class Retriever:

    def __init__(self):

        client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = client.get_collection(
            name=COLLECTION_NAME
        )

    def search(self, question, top_k=5):

        response = embed(
            model=EMBED_MODEL,
            input=question
        )

        query_embedding = response.embeddings[0]

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        results = []

        for i in range(len(result["documents"][0])):

            results.append(
                {
                    "text": result["documents"][0][i],
                    "metadata": result["metadatas"][0][i],
                    "distance": result["distances"][0][i],
                }
            )

        return results