"""
app.py
Streamlit chatbot UI — Wichita Public Schools District Data Q&A Assistant.
WPS brand colors: Navy #003087, Gold #FFB81C
Run: streamlit run app.py

Auto-ingest: if ChromaDB is empty on startup (e.g. fresh Streamlit Cloud deploy),
documents are generated and ingested automatically before the UI loads.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# ── Auto-ingest on first run ──────────────────────────────────────────────────
# On Streamlit Cloud, chroma_db/ doesn't exist — build it automatically.
def ensure_chroma_ready():
    import chromadb
    from chromadb.utils import embedding_functions

    chroma_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
    docs_dir   = os.path.join(os.path.dirname(__file__), "data", "documents")

    # Check if collection already has chunks
    try:
        client     = chromadb.PersistentClient(path=chroma_dir)
        embed_fn   = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_collection("district_docs", embedding_function=embed_fn)
        if collection.count() > 0:
            return  # already ingested, nothing to do
    except Exception:
        pass  # collection doesn't exist yet — fall through to ingest

    # Generate documents if missing
    if not os.path.exists(docs_dir) or len(os.listdir(docs_dir)) < 60:
        st.info("⚙️ First run — generating synthetic documents...")
        import generate_documents  # runs the script

    # Ingest into ChromaDB
    st.info("⚙️ Building vector index — this takes ~2 minutes on first run...")
    import glob, chromadb
    from chromadb.utils import embedding_functions

    embed_fn   = embedding_functions.DefaultEmbeddingFunction()
    client     = chromadb.PersistentClient(path=chroma_dir)

    try:
        client.delete_collection("district_docs")
    except Exception:
        pass

    collection = client.create_collection("district_docs", embedding_function=embed_fn)

    def chunk_text(text, chunk_size=300, overlap=50):
        words, chunks, start = text.split(), [], 0
        while start < len(words):
            chunks.append(" ".join(words[start:start + chunk_size]))
            start += chunk_size - overlap
        return chunks

    txt_files = glob.glob(os.path.join(docs_dir, "*.txt"))
    ids, documents, metadatas = [], [], []

    for filepath in txt_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        for i, chunk in enumerate(chunk_text(text)):
            ids.append(f"{filename}__chunk_{i}")
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk_index": i})

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    st.success(f"✅ Index ready — {len(ids)} chunks from {len(txt_files)} documents.")
    st.rerun()  # reload so the chat UI appears cleanly

ensure_chroma_ready()

# ── Now safe to import retriever and llm ─────────────────────────────────────
from retriever import retrieve
from llm import generate_answer

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WPS District Data Q&A",
    page_icon="🏫",
    layout="wide",
)

# ── Custom CSS — WPS brand colors + watermark ─────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f5f7fa;
}
[data-testid="stAppViewContainer"]::before {
    content: "USD 259  WPS  USD 259  WPS  USD 259  WPS";
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-25deg);
    font-size: 2.5rem;
    font-weight: 900;
    color: rgba(0, 48, 135, 0.04);
    white-space: nowrap;
    letter-spacing: 2rem;
    pointer-events: none;
    z-index: 0;
    width: 200vw;
    text-align: center;
    line-height: 5rem;
}
[data-testid="stSidebar"] {
    background-color: #003087 !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,184,28,0.3) !important;
}
.wps-header {
    background: linear-gradient(135deg, #003087 0%, #00205c 100%);
    color: white;
    padding: 1.2rem 1.8rem;
    border-radius: 12px;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    box-shadow: 0 4px 15px rgba(0,48,135,0.2);
}
.wps-badge {
    background: #FFB81C;
    color: #003087;
    font-size: 1.4rem;
    font-weight: 900;
    padding: 0.4rem 0.7rem;
    border-radius: 8px;
    letter-spacing: 1px;
    min-width: 56px;
    text-align: center;
    line-height: 1.3;
}
.wps-title { margin: 0; font-size: 1.4rem; font-weight: 700; }
.wps-sub   { margin: 0; font-size: 0.82rem; opacity: 0.8; margin-top: 2px; }
.ferpa-badge {
    background: #e8f4e8;
    border: 1px solid #4caf50;
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
    font-size: 0.75rem;
    color: #2e7d32;
    display: inline-block;
    margin-top: 0.5rem;
}
.stButton > button {
    background-color: #ffffff;
    color: #003087 !important;
    border: 1.5px solid rgba(255,255,255,0.4);
    border-radius: 8px;
    font-size: 0.78rem;
    padding: 0.35rem 0.6rem;
    width: 100%;
    text-align: left;
    white-space: normal;
    height: auto;
}
.stButton > button:hover {
    background-color: #FFB81C !important;
    color: #003087 !important;
    border-color: #FFB81C !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="wps-header">
    <div class="wps-badge">USD<br>259</div>
    <div>
        <p class="wps-title">🏫 Wichita Public Schools — District Data Q&A Assistant</p>
        <p class="wps-sub">AI-assisted self-service analytics for district leadership · Powered by RAG pipeline</p>
    </div>
</div>
<div class="ferpa-badge">🔒 FERPA-Safe · Synthetic documents only · No student PII · Local embeddings</div>
""", unsafe_allow_html=True)

st.markdown("")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏫 WPS Data Assistant")
    st.markdown("**USD 259 · Wichita, KS**")
    st.markdown("---")

    st.markdown("### 📂 Filter by Document Type")
    doc_filter = st.selectbox(
        "Document type",
        ["All Documents", "Assessment Rubrics", "Graduation Policies", "Program Evaluations"],
        label_visibility="collapsed",
    )
    filter_map = {
        "All Documents":        None,
        "Assessment Rubrics":   "assessment_rubric",
        "Graduation Policies":  "graduation_policy",
        "Program Evaluations":  "program_evaluation",
    }
    active_filter = filter_map[doc_filter]

    st.markdown("---")
    st.markdown("### 🔢 Results per Query")
    top_k = st.slider("Chunks to retrieve", min_value=3, max_value=10, value=5)

    st.markdown("---")
    st.markdown("### 💡 Sample Questions")

    sample_questions = [
        "What are the graduation credit requirements for College Preparatory?",
        "How did the STEM Academy perform against its benchmarks?",
        "What scoring levels are used in Mathematics assessment rubrics?",
        "What waiver provisions exist for graduation requirements?",
        "Which programs did not meet their participation rate targets?",
        "What recommendations were made for the Dual Language Program?",
        "What is the credit requirement for the IB pathway?",
        "How are performance tasks weighted in Science rubrics?",
    ]

    clicked_question = None
    for q in sample_questions:
        if st.button(q, key=f"sq_{q[:20]}"):
            clicked_question = q

    st.markdown("---")
    st.markdown("<small>Built with ChromaDB · OpenRouter · Streamlit<br>Portfolio project — synthetic data only</small>", unsafe_allow_html=True)

# ── Chat area ─────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg:
            with st.expander("📄 Source documents used"):
                for src in msg["sources"]:
                    st.write(f"• {src}")

question = clicked_question or st.chat_input("Ask a question about district policies or programs...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching district documents..."):
            chunks = retrieve(question, top_k=top_k)
            if active_filter:
                filtered = [c for c in chunks if c["source"].startswith(active_filter)]
                chunks = filtered if filtered else chunks
            answer  = generate_answer(question, chunks)
            sources = list(dict.fromkeys(c["source"] for c in chunks))

        st.markdown(answer)
        with st.expander("📄 Source documents used"):
            for src in sources:
                st.write(f"• {src}")

    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "sources": sources,
    })

if not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center; padding: 3rem; color: #888;'>
        <div style='font-size:3rem;'>🏫</div>
        <p style='font-size:1.1rem; font-weight:600; color:#003087;'>Ask a question to get started</p>
        <p style='font-size:0.85rem;'>Use the sample questions in the sidebar or type your own below.</p>
    </div>
    """, unsafe_allow_html=True)
