"""
evaluate.py
Runs 20 QA pairs through the RAG pipeline and scores on 3 metrics:
  - Faithfulness:        does the answer contain info from retrieved chunks?
  - Context Precision:   are retrieved chunks relevant to the question?
  - Context Recall:      does retrieved context cover the ground truth?

Uses cosine similarity via ChromaDB's embedding function — no extra API calls.
Run: python src/evaluate.py
Outputs: outputs/ragas_scorecard.csv and outputs/ragas_scorecard.png
"""

import time
import os
import sys
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")   # non-interactive backend — no display window needed
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from retriever import retrieve
from llm import generate_answer
from ragas_qa_pairs import QA_PAIRS
from chromadb.utils import embedding_functions

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Embedding function for similarity scoring ─────────────────────────────────
embed_fn = embedding_functions.DefaultEmbeddingFunction()

def cosine_similarity(a, b):
    """Cosine similarity between two embedding vectors — ranges 0 to 1."""
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

def score_faithfulness(answer: str, chunks: list[dict]) -> float:
    """
    Faithfulness: how similar is the answer embedding to the combined context?
    High score = answer stays close to what the documents say.
    """
    if not answer or not chunks:
        return 0.0
    context = " ".join(c["text"] for c in chunks)
    ans_emb  = embed_fn([answer])[0]
    ctx_emb  = embed_fn([context])[0]
    return round(cosine_similarity(ans_emb, ctx_emb), 4)

def score_context_precision(question: str, chunks: list[dict], doc_type: str) -> float:
    """
    Context Precision: what fraction of retrieved chunks are from the right document type?
    e.g. graduation question → graduation_policy chunks = relevant.
    """
    if not chunks:
        return 0.0
    relevant = sum(1 for c in chunks if c["source"].startswith(doc_type))
    return round(relevant / len(chunks), 4)

def score_context_recall(ground_truth: str, chunks: list[dict]) -> float:
    """
    Context Recall: how similar is the combined context to the ground truth answer?
    High score = the retrieved chunks contain the information needed to answer.
    """
    if not chunks or not ground_truth:
        return 0.0
    context = " ".join(c["text"] for c in chunks)
    gt_emb  = embed_fn([ground_truth])[0]
    ctx_emb = embed_fn([context])[0]
    return round(cosine_similarity(gt_emb, ctx_emb), 4)

# ── Run evaluation ────────────────────────────────────────────────────────────
print(f"Running evaluation on {len(QA_PAIRS)} QA pairs...\n")

results = []
for i, pair in enumerate(QA_PAIRS):
    print(f"  [{i+1:02d}/{len(QA_PAIRS)}] {pair['question'][:65]}...")

    chunks = retrieve(pair["question"], top_k=5)
    try:
        answer = generate_answer(pair["question"], chunks)
    except Exception as e:
        print(f"    ⚠️ Skipped — {e}")
    answer = "I could not find that information in the district documents."
    time.sleep(4)   # 3 second pause between calls to avoid rate limiting

    faith  = score_faithfulness(answer, chunks)
    prec   = score_context_precision(pair["question"], chunks, pair["doc_type"])
    recall = score_context_recall(pair["ground_truth"], chunks)

    results.append({
        "question":          pair["question"],
        "doc_type":          pair["doc_type"],
        "faithfulness":      faith,
        "context_precision": prec,
        "context_recall":    recall,
        "answer_preview":    answer[:120].replace("\n", " "),
    })

# ── Save CSV ──────────────────────────────────────────────────────────────────
csv_path = os.path.join(OUTPUT_DIR, "ragas_scorecard.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
print(f"\n✅ Scorecard saved: {csv_path}")

# ── Compute averages ──────────────────────────────────────────────────────────
avg_faith  = round(np.mean([r["faithfulness"]      for r in results]), 4)
avg_prec   = round(np.mean([r["context_precision"] for r in results]), 4)
avg_recall = round(np.mean([r["context_recall"]    for r in results]), 4)

print(f"\n{'='*45}")
print(f"  RAGAS SCORECARD SUMMARY")
print(f"{'='*45}")
print(f"  Faithfulness:      {avg_faith:.4f}")
print(f"  Context Precision: {avg_prec:.4f}")
print(f"  Context Recall:    {avg_recall:.4f}")
print(f"{'='*45}\n")

# ── Bar chart ─────────────────────────────────────────────────────────────────
metrics = ["Faithfulness", "Context\nPrecision", "Context\nRecall"]
scores  = [avg_faith, avg_prec, avg_recall]
colors  = ["#003087", "#FFB81C", "#4caf50"]   # WPS navy, gold, green

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(metrics, scores, color=colors, width=0.45, edgecolor="white", linewidth=1.5)

# Add score labels on top of each bar
for bar, score in zip(bars, scores):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{score:.3f}",
        ha="center", va="bottom", fontsize=13, fontweight="bold", color="#333"
    )

ax.set_ylim(0, 1.15)
ax.set_ylabel("Score (0–1)", fontsize=11)
ax.set_title(
    "RAGAS Evaluation — District RAG Assistant\nWichita Public Schools (Synthetic Data)",
    fontsize=12, fontweight="bold", pad=15
)
ax.axhline(y=0.7, color="gray", linestyle="--", linewidth=1, alpha=0.5, label="0.7 target")
ax.legend(fontsize=9)
ax.set_facecolor("#f9f9f9")
fig.patch.set_facecolor("white")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

png_path = os.path.join(OUTPUT_DIR, "ragas_scorecard.png")
plt.tight_layout()
plt.savefig(png_path, dpi=150)
plt.close()
print(f"✅ Chart saved: {png_path}")
