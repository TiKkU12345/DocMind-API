import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="DocMind",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
    body { background-color: #0f1117; }
    .main { background-color: #0f1117; }

    .title-block {
        padding: 2rem 0 1rem 0;
        border-bottom: 1px solid #2a2d3a;
        margin-bottom: 2rem;
    }
    .title-text {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .subtitle-text {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0.2rem;
    }
    .answer-box {
        background-color: #1a1d27;
        border-left: 3px solid #6366f1;
        border-radius: 6px;
        padding: 1.2rem 1.5rem;
        color: #e5e7eb;
        font-size: 0.97rem;
        line-height: 1.7;
        margin-top: 1rem;
    }
    .source-box {
        background-color: #13151f;
        border: 1px solid #2a2d3a;
        border-radius: 6px;
        padding: 0.9rem 1.2rem;
        color: #9ca3af;
        font-size: 0.85rem;
        line-height: 1.6;
        margin-bottom: 0.5rem;
        font-family: monospace;
    }
    .status-ok {
        color: #10b981;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .status-err {
        color: #ef4444;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .stButton > button {
        background-color: #6366f1;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #4f46e5;
        color: white;
    }
    section[data-testid="stSidebar"] {
        background-color: #13151f;
        border-right: 1px solid #2a2d3a;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🧠 DocMind")
    st.markdown("---")

    st.markdown("#### Upload Document")
    uploaded_file = st.file_uploader(
        "PDF or TXT only",
        type=["pdf", "txt"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        if st.button("Index Document"):
            with st.spinner("Chunking & embedding..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.markdown(f'<p class="status-ok">✓ Indexed — {data["chunks_created"]} chunks</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p class="status-err">✗ {response.json().get("detail", "Upload failed")}</p>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<p class="status-err">✗ Backend not reachable</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Health check
    try:
        health = requests.get(f"{API_BASE}/health", timeout=2)
        if health.status_code == 200:
            st.markdown('<p class="status-ok">● Backend running</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-err">● Backend error</p>', unsafe_allow_html=True)
    except:
        st.markdown('<p class="status-err">● Backend offline</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    top_k = st.slider("Chunks to retrieve (top-k)", min_value=1, max_value=10, value=3)

# Main area
st.markdown("""
<div class="title-block">
    <div class="title-text">DocMind</div>
    <div class="subtitle-text">Ask questions about your uploaded documents</div>
</div>
""", unsafe_allow_html=True)

query = st.text_input(
    "Your question",
    placeholder="e.g. What is the leave policy?",
    label_visibility="collapsed"
)

if st.button("Ask"):
    if not query.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Retrieving and generating answer..."):
            try:
                response = requests.post(
                    f"{API_BASE}/query",
                    json={"query": query, "top_k": top_k}
                )
                if response.status_code == 200:
                    data = response.json()

                    st.markdown("**Answer**")
                    st.markdown(f'<div class="answer-box">{data["answer"]}</div>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.expander(f"Source chunks used ({len(data['sources'])})"):
                        for i, chunk in enumerate(data["sources"], 1):
                            st.markdown(f'<div class="source-box"><b>Chunk {i}</b><br>{chunk}</div>', unsafe_allow_html=True)

                elif response.status_code == 404:
                    st.warning("No documents indexed yet. Upload a document first.")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Something went wrong')}")

            except Exception:
                st.error("Backend not reachable. Make sure uvicorn is running.")