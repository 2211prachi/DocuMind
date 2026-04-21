import streamlit as st
import requests
import time
import base64
from pathlib import Path

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind — AI Document Q&A",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Backend URL ─────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

# ─── Load Logo ───────────────────────────────────────────────────────────────
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

def get_logo_base64():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()

# ─── Premium CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Typography ───────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hide default Streamlit elements ──────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Main background ─────────────────────────── */
    .stApp {
        background: linear-gradient(160deg, #0a0a1a 0%, #0d1117 40%, #111827 100%);
    }

    /* ── Hero header ─────────────────────────────── */
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.12) 50%, rgba(236, 72, 153, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        backdrop-filter: blur(20px);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(99, 102, 241, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 70% 50%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
        animation: shimmer 8s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { transform: translateX(-10%) rotate(0deg); }
        50% { transform: translateX(10%) rotate(2deg); }
    }
    .hero-logo {
        width: 72px;
        height: 72px;
        border-radius: 16px;
        object-fit: cover;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
        border: 2px solid rgba(99, 102, 241, 0.3);
        position: relative;
        z-index: 1;
    }
    .hero-text {
        position: relative;
        z-index: 1;
    }
    .hero-text h1 {
        margin: 0;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #c7d2fe, #a78bfa, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-text p {
        margin: 0.3rem 0 0;
        font-size: 0.95rem;
        color: rgba(203, 213, 225, 0.7);
        font-weight: 300;
        letter-spacing: 0.5px;
    }

    /* ── Sidebar ──────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f23 0%, #13132b 50%, #0d1117 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.1);
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        background: linear-gradient(135deg, #a78bfa, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.3rem;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }

    /* ── Sidebar logo block ───────────────────────── */
    .sidebar-logo-section {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 1rem 0.5rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid rgba(99, 102, 241, 0.1);
    }
    .sidebar-logo-section img {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    .sidebar-logo-section .brand-name {
        font-size: 1.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c7d2fe, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── Upload button ────────────────────────────── */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }

    /* ── File chip (uploaded files list) ───────────── */
    .file-chip {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 10px;
        padding: 0.5rem 0.8rem;
        margin: 0.3rem 0;
        font-size: 0.82rem;
        color: #c7d2fe;
        transition: all 0.2s ease;
    }
    .file-chip:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: rgba(99, 102, 241, 0.3);
    }
    .file-chip .icon { font-size: 1rem; }

    /* ── Chat messages ────────────────────────────── */
    [data-testid="stChatMessage"] {
        background: rgba(15, 15, 35, 0.6) !important;
        border: 1px solid rgba(99, 102, 241, 0.08) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
    }

    /* ── Metric cards ─────────────────────────────── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.05));
        border: 1px solid rgba(99, 102, 241, 0.12);
        border-radius: 14px;
        padding: 1rem;
        text-align: center;
    }
    [data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #a78bfa, #c084fc) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }

    /* ── Source chip ───────────────────────────────── */
    .source-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.08));
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 0.45rem 0.85rem;
        margin: 0.25rem;
        font-size: 0.8rem;
        color: #c7d2fe;
        transition: all 0.2s ease;
    }
    .source-chip:hover {
        background: rgba(99, 102, 241, 0.2);
        transform: translateY(-1px);
    }

    /* ── Expander ─────────────────────────────────── */
    .streamlit-expanderHeader {
        background: rgba(99, 102, 241, 0.05) !important;
        border-radius: 10px !important;
        color: #a78bfa !important;
        font-weight: 500 !important;
    }

    /* ── Chat input ───────────────────────────────── */
    [data-testid="stChatInput"] textarea {
        background: rgba(15, 15, 35, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 14px !important;
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.15) !important;
    }

    /* ── Empty state ──────────────────────────────── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #475569;
    }
    .empty-state .icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.4;
    }
    .empty-state h3 {
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .empty-state p {
        color: #475569;
        font-size: 0.9rem;
        max-width: 400px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Status badge ─────────────────────────────── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.2);
        color: #4ade80;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #4ade80;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ── Dividers ─────────────────────────────────── */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(99, 102, 241, 0.1) !important;
        margin: 1rem 0 !important;
    }

    /* ── Selectbox ────────────────────────────────── */
    .stSelectbox > div > div {
        background: rgba(15, 15, 35, 0.6) !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        border-radius: 10px !important;
    }

    /* ── Force dark on ALL containers ─────────────── */
    .stApp, .main, .block-container,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .stChatFloatingInputContainer,
    div[data-testid="stChatInput"] > div {
        background-color: #0a0a1a !important;
        background: #0a0a1a !important;
    }

    /* ── Chat input wrapper ───────────────────────── */
    [data-testid="stBottomBlockContainer"] {
        background: linear-gradient(180deg, transparent 0%, #0a0a1a 15%) !important;
        border-top: 1px solid rgba(99, 102, 241, 0.08) !important;
    }

    [data-testid="stChatInput"] {
        background: transparent !important;
    }

    [data-testid="stChatInput"] > div {
        background: rgba(15, 15, 35, 0.95) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 14px !important;
    }

    /* ── Send button in chat input ─────────────────── */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
    }

    /* ── File uploader ────────────────────────────── */
    [data-testid="stFileUploader"] {
        background: rgba(15, 15, 35, 0.4) !important;
        border: 1px dashed rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section {
        background: transparent !important;
    }
    [data-testid="stFileUploader"] button {
        background: rgba(99, 102, 241, 0.15) !important;
        color: #c7d2fe !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "active_file" not in st.session_state:
    st.session_state.active_file = None

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand header
    if logo_b64:
        st.markdown(f"""
        <div class="sidebar-logo-section">
            <img src="data:image/png;base64,{logo_b64}" alt="DocuMind">
            <span class="brand-name">DocuMind</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-logo-section">
            <span style="font-size:1.8rem;">🧠</span>
            <span class="brand-name">DocuMind</span>
        </div>
        """, unsafe_allow_html=True)

    # Connection status
    try:
        health = requests.get(f"{API_URL}/", timeout=3)
        if health.status_code == 200:
            st.markdown('<div class="status-badge"><div class="status-dot"></div>Backend Connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge" style="border-color:rgba(239,68,68,0.2);color:#f87171;background:rgba(239,68,68,0.1);"><div class="status-dot" style="background:#f87171;"></div>Backend Error</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown('<div class="status-badge" style="border-color:rgba(239,68,68,0.2);color:#f87171;background:rgba(239,68,68,0.1);"><div class="status-dot" style="background:#f87171;animation:none;"></div>Backend Offline</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📄 Upload Documents")
    st.caption("Upload PDF files to build your knowledge base.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file and st.button("⬆️ Upload & Process", use_container_width=True):
        with st.spinner("Processing PDF…"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                resp = requests.post(f"{API_URL}/upload", files=files, timeout=120)
                data = resp.json()

                if "error" in data:
                    st.error(f"❌ {data['error']}")
                else:
                    st.success(f"✅ **{data['filename']}** processed!")
                    col1, col2 = st.columns(2)
                    col1.metric("Pages", data["pages"])
                    col2.metric("Chunks", data["chunks"])
                    if data["filename"] not in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.append(data["filename"])
                    st.session_state.active_file = data["filename"]
                    st.rerun()
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot reach the backend. Make sure FastAPI is running on port 8000.")
            except Exception as e:
                st.error(f"⚠️ {e}")

    # Uploaded files list
    if st.session_state.uploaded_files:
        st.markdown("---")
        st.markdown("### 📚 Documents")
        for f in st.session_state.uploaded_files:
            st.markdown(f'<div class="file-chip"><span class="icon">📄</span>{f}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Query Settings")

    file_options = ["All Documents"] + st.session_state.uploaded_files
    if st.session_state.active_file and st.session_state.active_file in file_options:
        default_idx = file_options.index(st.session_state.active_file)
    elif len(file_options) > 1:
        default_idx = len(file_options) - 1
    else:
        default_idx = 0

    selected_file = st.selectbox(
        "🔍 Search in document",
        options=file_options,
        index=default_idx,
        help="Queries will be scoped to this document.",
    )
    filename_filter = selected_file if selected_file != "All Documents" else ""

    st.markdown("")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ─── Main Area ───────────────────────────────────────────────────────────────

# Hero header with logo
if logo_b64:
    st.markdown(f"""
    <div class="hero-container">
        <img src="data:image/png;base64,{logo_b64}" class="hero-logo" alt="DocuMind">
        <div class="hero-text">
            <h1>DocuMind</h1>
            <p>AI-powered document analysis &amp; question answering</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-text">
            <h1>🧠 DocuMind</h1>
            <p>AI-powered document analysis &amp; question answering</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Empty state ──────────────────────────────────────────────────────────────
if not st.session_state.chat_history:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">💬</div>
        <h3>Start a Conversation</h3>
        <p>Upload a PDF document using the sidebar, then ask questions about its content below.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Render chat history ──────────────────────────────────────────────────────
for entry in st.session_state.chat_history:
    with st.chat_message("user", avatar="👤"):
        st.markdown(entry["question"])

    with st.chat_message("assistant", avatar="🧠"):
        st.markdown(entry["answer"])

        metrics = entry.get("metrics", {})
        confidence = entry.get("confidence", 0)

        cols = st.columns(3)
        cols[0].metric("Confidence", f"{confidence * 100:.0f}%")
        cols[1].metric("Chunks Used", metrics.get("chunks_used", "—"))
        cols[2].metric("Retrieval", f"{metrics.get('retrieval_time', 0):.2f}s")

        sources = entry.get("sources", [])
        if sources:
            with st.expander("📑 View Sources"):
                for src in sources:
                    page = src.get("page", "?")
                    fname = src.get("file", "unknown")
                    st.markdown(
                        f'<span class="source-chip">📄 {fname} — Page {page}</span>',
                        unsafe_allow_html=True,
                    )

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask a question about your documents…"):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Thinking…"):
            try:
                payload = {"question": prompt}
                if filename_filter:
                    payload["filename"] = filename_filter

                resp = requests.post(f"{API_URL}/query", json=payload, timeout=120)
                data = resp.json()

                answer = data.get("answer", "No answer returned.")
                confidence = data.get("confidence", 0)
                metrics = data.get("metrics", {})
                sources = data.get("sources", [])

                st.markdown(answer)

                cols = st.columns(3)
                cols[0].metric("Confidence", f"{confidence * 100:.0f}%")
                cols[1].metric("Chunks Used", metrics.get("chunks_used", "—"))
                cols[2].metric("Retrieval", f"{metrics.get('retrieval_time', 0):.2f}s")

                if sources:
                    with st.expander("📑 View Sources"):
                        for src in sources:
                            page = src.get("page", "?")
                            fname = src.get("file", "unknown")
                            st.markdown(
                                f'<span class="source-chip">📄 {fname} — Page {page}</span>',
                                unsafe_allow_html=True,
                            )

                st.session_state.chat_history.append({
                    "question": prompt,
                    "answer": answer,
                    "confidence": confidence,
                    "metrics": metrics,
                    "sources": sources,
                })

            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot reach the backend. Make sure FastAPI is running on port 8000.")
            except Exception as e:
                st.error(f"⚠️ {e}")
