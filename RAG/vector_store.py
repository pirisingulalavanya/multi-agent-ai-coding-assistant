import pickle
import os
import math
from loguru import logger

CHUNKS_PATH = "data/faiss/chunks.pkl"

class VectorStore:
    def __init__(self):
        self.chunks = []
        os.makedirs("data/faiss", exist_ok=True)

    def add_documents(self, chunks: list):
        logger.info(f"Adding {len(chunks)} chunks...")
        self.chunks.extend(chunks)
        self.save()
        logger.info(f"Total chunks: {len(self.chunks)}")

    def search(self, query: str, k: int = 4) -> list:
        if not self.chunks:
            return []
        query_words = set(query.lower().split())
        scores = []
        for i, chunk in enumerate(self.chunks):
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words & chunk_words)
            scores.append((overlap, i))
        scores.sort(reverse=True)
        return [self.chunks[i] for _, i in scores[:k]]

    def save(self):
        with open(CHUNKS_PATH, "wb") as f:
            pickle.dump(self.chunks, f)

    def load(self):
        if os.path.exists(CHUNKS_PATH):
            with open(CHUNKS_PATH, "rb") as f:
                self.chunks = pickle.load(f)
            logger.info(f"Loaded {len(self.chunks)} chunks")

    def clear(self):
        self.chunks = []
        if os.path.exists(CHUNKS_PATH):
            os.remove(CHUNKS_PATH)
        logger.info("Vector store cleared")

vector_store = VectorStore()
vector_store.load()