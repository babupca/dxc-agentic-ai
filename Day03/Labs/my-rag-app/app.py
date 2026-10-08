import io
import json
import sys
from pathlib import Path

import numpy as np
import streamlit as st
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from askit_core import bedrock, config

st.set_page_config(page_title="PDF Buddy", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #0b1020, #101a2b 50%, #1a1a2e); color: #eaf2ff; }
    .block-container { padding-top: 1.5rem; }
    h1 { color: #58d6c7; }
    .stButton > button { border-radius: 12px; background: #58d6c7; color: #08151d; font-weight: 600; }
    .stDownloadButton > button { border-radius: 12px; background: #9d7bff; color: white; }
    [data-testid="stChatMessage"] { border-radius: 16px; }
    .stSidebar > div { background: #111827; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PDF Buddy")
st.caption("Upload. Ask. Done.")


if not config.SMALL_MODEL:
    st.warning("Set BEDROCK_SMALL_MODEL_ID in the project .env before running this app.")
    st.stop()


@st.cache_resource
def get_client():
    return bedrock.client()


def cosine(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def chunk_text_by_words(text, size=120, overlap=30):
    words = text.split()
    if not words:
        return []
    step = max(1, size - overlap)
    chunks = []
    for i in range(0, len(words), step):
        piece = words[i : i + size]
        if piece:
            chunks.append(" ".join(piece))
    return chunks


def embed_texts(texts):
    client = get_client()
    vectors = []
    for i in range(0, len(texts), 4):
        batch = texts[i : i + 4]
        try:
            out = []
            for text in batch:
                body = json.dumps({"inputText": text, "dimensions": 512, "normalize": True})
                resp = client.invoke_model(modelId="amazon.titan-embed-text-v2:0", body=body)
                payload = json.loads(resp["body"].read())
                out.append(payload["embedding"])
            vectors.extend(out)
        except Exception:
            st.error("AWS embedding failed. Check .env keys, AWS region, and Titan model access.")
            return []
    return vectors


def build_index(file_obj, chunk_size, overlap):
    reader = PdfReader(io.BytesIO(file_obj.read()))
    pages = []
    for page_no, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((page_no, text))
    if not pages:
        return []

    records = []
    for page_no, text in pages:
        for chunk in chunk_text_by_words(text, chunk_size, overlap):
            records.append({"page": page_no, "text": chunk.strip()})

    texts = [r["text"] for r in records]
    vectors = embed_texts(texts)
    if len(vectors) != len(records):
        return []

    for rec, vec in zip(records, vectors):
        rec["vector"] = np.array(vec, dtype=float)
    return records


def ask_question(question, top_k):
    client = get_client()
    q_vec = embed_texts([question])
    if not q_vec:
        return None, []
    q_vec = np.asarray(q_vec[0], dtype=float)
    hits = []
    for rec in st.session_state.index:
        hits.append({
            "page": rec["page"],
            "text": rec["text"],
            "score": cosine(q_vec, rec["vector"]),
        })
    hits = sorted(hits, key=lambda x: x["score"], reverse=True)[:top_k]
    context = "\n\n".join(f"[p.{h['page']}]: {h['text']}" for h in hits)
    prompt = (
        "Answer ONLY from the context. If the answer is not in the context, say you could not find it in the PDF. "
        "Cite the page like [p.3].\n\nContext:\n"
        f"{context}\n\nQuestion: {question}"
    )
    try:
        resp = client.converse(
            modelId=config.SMALL_MODEL,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 500, "temperature": 0.2},
        )
        answer = resp["output"]["message"]["content"][0]["text"]
        return answer, hits
    except Exception:
        st.error("AWS chat failed. Check .env keys, region, and model access. Please try again.")
        return None, hits


with st.sidebar:
    st.header("About me")
    st.info("Built by Babu\n\nToday: 2026-10-07\n\nFun line: Good code is a calm teammate.")
    st.subheader("Controls")
    top_k = st.slider("Top-K", 1, 6, 3)
    chunk_size = st.slider("Chunk size", 60, 220, 120)
    overlap = st.slider("Overlap", 10, 80, 30)
    if st.button("Clear chat"):
        st.session_state.chat = []

pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])

if st.button("Build index"):
    if pdf_file is None:
        st.warning("Upload a PDF first.")
    else:
        st.session_state.index = build_index(pdf_file, chunk_size, overlap)
        st.session_state.chat = []
        if st.session_state.index:
            st.success(f"Indexed {len(st.session_state.index)} chunks from the PDF.")
        else:
            st.warning("No text found in this PDF. Please upload a PDF with selectable text.")

if "index" not in st.session_state:
    st.session_state.index = []
if "chat" not in st.session_state:
    st.session_state.chat = []

if st.session_state.index:
    chat_container = st.container(height=520)
    with chat_container:
        for msg in st.session_state.chat:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["text"])
            else:
                with st.chat_message("assistant"):
                    best_score = max((h["score"] for h in msg.get("hits", [])), default=0.0)
                    badge = "grounded" if best_score >= 0.35 else "weak match"
                    st.markdown(f"<span style='font-size: 12px; background:#1f2937; color:#b6f4eb; padding:4px 8px; border-radius:999px;'>{badge}</span>", unsafe_allow_html=True)
                    st.write(msg["text"])
                    with st.expander("Sources"):
                        for hit in msg.get("hits", []):
                            st.write(f"Page {hit['page']} | score {hit['score']:.2f} | {hit['text']}")

    question = st.chat_input("Ask a question about the PDF")
    if question:
        answer, hits = ask_question(question, top_k)
        if answer:
            st.session_state.chat.append({"role": "user", "text": question})
            st.session_state.chat.append({"role": "assistant", "text": answer, "hits": hits})
            st.rerun()

    if st.button("Not in my PDF?"):
        q = "Who won the last cricket world cup?"
        answer, hits = ask_question(q, top_k)
        if answer:
            st.write("Assistant:")
            st.write(answer)
            st.write("This answer is outside the PDF context, so the app should say it was not found.")

chat_md = "\n\n".join(
    f"{msg['role']}: {msg['text']}" if msg["role"] == "user" else f"assistant: {msg['text']}"
    for msg in st.session_state.chat
)
if st.download_button("Download chat as .md", chat_md, file_name="chat.md"):
    pass

st.caption("Built by Babu with vibe coding at DevPro Academy")
