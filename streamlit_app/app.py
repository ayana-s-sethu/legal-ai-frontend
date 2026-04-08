import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Page config
st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS (better UI)
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.big-title {
    font-size: 42px;
    font-weight: bold;
    color: #4CAF50;
}
.card {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="big-title">⚖️ Legal AI Assistant</p>', unsafe_allow_html=True)
st.write("Analyze legal documents with AI-powered insights.")

# Layout
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("📄 Upload Document", type=["pdf", "txt"])

with col2:
    question = st.text_input("❓ Ask your question")

# Features
mode = st.checkbox("📚 Beginner Mode (Simple Explanation)")
show_preview = st.checkbox("👁 Show Document Preview")
save_history = st.checkbox("💾 Save Chat History")

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

if uploaded_file and question:
    content = ""

    # Read file
    if uploaded_file.type == "application/pdf":
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            content += page.extract_text() or ""
    else:
        content = uploaded_file.read().decode("utf-8")

    # Beginner mode
    extra = "Explain in very simple terms." if mode else ""

    # Prompt
    prompt = f"""
You are a Professional Legal Document Assistant.

Rules:
- Answer ONLY using the document
- Do NOT hallucinate
- Be clear and structured

{extra}

Document:
{content[:3000]}

Question:
{question}

Format:
Summary:
Detailed Explanation:
Direct Quote:
Reference:
"""

    # AI response (with fallback model)
    with st.spinner("⚖️ Analyzing document..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
        except:
            # fallback model (no crash)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

    answer = response.choices[0].message.content

    # Save history
    if save_history:
        st.session_state.history.append((question, answer))

    # Display answer
    st.subheader("📄 Answer")
    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

    # Download
    st.download_button("📥 Download Answer", answer)

    # Document preview
    if show_preview:
        st.subheader("📄 Document Preview")
        st.write(content[:1000])

# Show history
if save_history and st.session_state.history:
    st.subheader("🧠 Chat History")
    for q, a in st.session_state.history:
        st.write("**Q:**", q)
        st.write("**A:**", a)
        st.markdown("---")