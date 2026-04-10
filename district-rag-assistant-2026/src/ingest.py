"""
ingest.py
Loads all .txt files from data/documents/, splits into chunks,
embeds using ChromaDB's built-in embedding function (no torch needed).
Run: python src/ingest.py
Output: chroma_db/ folder created with all embeddings stored
"""

import os
import glob
import chromadb
from chromadb.utils import embedding_functions

# ── Config ───────────────────────────────────────────────────────────────────
DOCS_DIR      = "data/documents"
CHROMA_DIR    = "chroma_db"
COLLECTION    = "district_docs"
CHUNK_SIZE    = 300   # words per chunk
CHUNK_OVERLAP = 50    # words shared between adjacent chunks

# ── Embedding function — uses chromadb's default (onnx-based, no torch) ─────
embed_fn = embedding_functions.DefaultEmbeddingFunction()

# ── Connect to local ChromaDB ────────────────────────────────────────────────
client = chromadb.PersistentClient(path=CHROMA_DIR)

# Clear existing collection if re-running
existing = [c.name for c in client.list_collections()]
if COLLECTION in existing:
    client.delete_collection(COLLECTION)
    print("Cleared existing collection.")

collection = client.create_collection(
    name=COLLECTION,
    embedding_function=embed_fn   # attach embedding function to collection
)

# ── Chunking function ────────────────────────────────────────────────────────
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end   = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap    # step forward, keeping overlap words
    return chunks

# ── Process each document ────────────────────────────────────────────────────
txt_files = glob.glob(os.path.join(DOCS_DIR, "*.txt"))
print(f"Found {len(txt_files)} documents. Chunking and embedding...")

total_chunks = 0
ids, documents, metadatas = [], [], []

for filepath in txt_files:
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        ids.append(f"{filename}__chunk_{i}")
        documents.append(chunk)
        metadatas.append({"source": filename, "chunk_index": i})

    total_chunks += len(chunks)

# ── Insert all chunks at once (420 chunks is small enough) ───────────────────
print(f"Inserting {total_chunks} chunks...")
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
)
print(f"✅ Done — {total_chunks} chunks from {len(txt_files)} documents stored in ChromaDB.")
print(f"   Collection: '{COLLECTION}'  |  Path: {CHROMA_DIR}/")
