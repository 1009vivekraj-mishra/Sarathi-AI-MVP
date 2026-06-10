import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
# Backend imports
from backend.assistant import get_answer_and_sources
from backend.learning_engine import generate_learning_suggestions
from backend.skill_tracker import get_or_create_user, update_skill, get_skill_profile

st.set_page_config(page_title="Sarathi AI", layout="centered", page_icon=":robot:")

# Custom CSS for dark theme
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stButton>button {
        background-color: #00bcd4;
        color: #ffffff;
        border: none;
        border-radius: 4px;
    }
    .stTextInput input {
        background-color: #1e2229;
        color: #e0e0e0;
        border: 1px solid #00bcd4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Sarathi AI – Workforce Intelligence Assistant")

# Sidebar for uploads
with st.sidebar:
    st.header("Upload Files")
    # SOP / manual upload
    doc_file = st.file_uploader("Upload SOP / Manual (PDF or TXT)", type=["pdf", "txt"])
    if doc_file:
        save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "documents"))
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, doc_file.name)
        with open(save_path, "wb") as f:
            f.write(doc_file.getbuffer())
        st.success(f"Saved document: {doc_file.name}")
        # Rebuild vector store
        from backend import rag as rag_mod
        if os.path.isdir(rag_mod.VECTOR_DIR):
            import shutil; shutil.rmtree(rag_mod.VECTOR_DIR)
        rag_mod._get_vector_store()
    # Expert note upload
    exp_file = st.file_uploader("Upload Expert Note (PDF or TXT)", type=["pdf", "txt"])
    if exp_file:
        save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "expert"))
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, exp_file.name)
        with open(save_path, "wb") as f:
            f.write(exp_file.getbuffer())
        st.success(f"Saved expert note: {exp_file.name}")
        from backend import rag as rag_mod
        if os.path.isdir(rag_mod.VECTOR_DIR):
            import shutil; shutil.rmtree(rag_mod.VECTOR_DIR)
        rag_mod._get_vector_store()
# Simple user session state
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

if st.session_state["user_name"] is None:
    st.session_state["user_name"] = st.text_input("Enter your name", "")
    if not st.session_state["user_name"]:
        st.stop()

user_id, _ = get_or_create_user(st.session_state["user_name"])

query = st.text_input("Ask Sarathi about your work or SOP…", "")
if st.button("Submit") and query:
    with st.spinner("Thinking…"):
        answer, sources = get_answer_and_sources(query)
        # Simple skill categorization (placeholder)
        skill_category = "general"
        update_skill(user_id, skill_category)
        suggestions = generate_learning_suggestions(sources)
    st.subheader("Answer")
    st.write(answer)
    if sources:
        st.caption("Sources: " + ", ".join(sources))
    if suggestions:
        st.subheader("Learning Suggestions")
        for s in suggestions:
            st.write("- " + s)
    st.caption("Skill profile updated.")

# Show simple skill exposure table (optional)
if st.checkbox("Show my skill exposure"):
    profile = get_skill_profile(user_id)
    if profile:
        for skill, exp in profile:
            st.write(f"{skill}: {exp}")
    else:
        st.write("No skill data yet.")
