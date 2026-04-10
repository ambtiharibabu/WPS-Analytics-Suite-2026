"""
retriever.py
Takes a natural language question, searches ChromaDB for the most
relevant chunks, and returns them with source filenames.
Can be run directly to test: python src/retriever.py
"""

import chromadb
from chromadb.utils import embedding_functions

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_DIR = "chroma_db"
COLLECTION = "district_docs"
TOP_K      = 5   # number of chunks to retrieve per query

# ── Connect to the same local ChromaDB we built in ingest.py ─────────────────
embed_fn = embedding_functions.DefaultEmbeddingFunction()
client     = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(name=COLLECTION, embedding_function=embed_fn)


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    """
    Query ChromaDB with a natural language question.
    Returns a list of dicts: [{"text": ..., "source": ..., "chunk_index": ...}]
    """
    results = collection.query(
        query_texts=[question],   # ChromaDB embeds the question automatically
        n_results=top_k,
    )

    chunks = []
    for i in range(len(results["documents"][0])):   # results are nested in a list
        chunks.append({
            "text":        results["documents"][0][i],
            "source":      results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
        })
    return chunks


# ── Quick test when run directly ──────────────────────────────────────────────
if __name__ == "__main__":
    test_questions = [
        "What are the graduation credit requirements for the College Preparatory pathway?",
        "How is the STEM Academy program performing against its benchmarks?",
        "What scoring levels are used in Mathematics assessment rubrics?",
    ]

    for question in test_questions:
        print(f"\nQ: {question}")
        print("-" * 60)
        chunks = retrieve(question)
        for i, chunk in enumerate(chunks):
            print(f"  [{i+1}] Source: {chunk['source']}")
            print(f"       Preview: {chunk['text'][:120]}...")
        print()
