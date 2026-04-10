"""
llm.py
Sends retrieved context chunks + user question to OpenRouter LLM.
The LLM is instructed to answer ONLY from the provided context.
Can be tested directly: python src/llm.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loads OPENROUTER_API_KEY from .env file in project root

# ── Config ────────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL              = "openrouter/free"
API_URL            = "https://openrouter.ai/api/v1/chat/completions"

# ── System prompt — grounds the LLM to context only ──────────────────────────
SYSTEM_PROMPT = """You are a helpful data assistant for Wichita Public Schools district leadership.
Answer questions using ONLY the context documents provided below.
If the answer is not found in the context, say: "I could not find that information in the district documents."
Do not reference or infer any individual student data.
Be concise and cite the source document name when possible."""


def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    Takes a question and list of retrieved chunks (from retriever.py).
    Returns the LLM's answer as a string.
    """
    if not OPENROUTER_API_KEY:
        return "❌ OPENROUTER_API_KEY not set. Add it to your .env file."

    # Build context block from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(f"[Source {i+1}: {chunk['source']}]\n{chunk['text']}")
    context_text = "\n\n".join(context_parts)

    user_message = f"""Context documents:
{context_text}

Question: {question}

Answer based only on the context above:"""

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            "max_tokens": 500,
            "temperature": 0.2,
        },
        timeout=60,
    )

    if response.status_code != 200:
        return f"❌ API error {response.status_code}: {response.text}"

    content = response.json()["choices"][0]["message"]["content"]
    if content is None:
        return "I could not find that information in the district documents."
    return content.strip()


# ── Quick test when run directly ──────────────────────────────────────────────
if __name__ == "__main__":
    from retriever import retrieve

    question = "What are the graduation credit requirements for the College Preparatory pathway?"
    print(f"Q: {question}\n")

    chunks = retrieve(question)
    answer = generate_answer(question, chunks)

    print(f"A: {answer}\n")
    print("Sources used:")
    for chunk in chunks:
        print(f"  - {chunk['source']}")
