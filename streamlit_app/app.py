import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Page config
st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide"
)

# UI Styling
st.markdown("""
<style>
.big-title {
    font-size: 40px;
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
st.markdown('<p class="big-title">⚖️ Legal AI Assistant (Strict RAG)</p>', unsafe_allow_html=True)
st.write("Upload a legal document and ask questions strictly based on it.")

# Upload
uploaded_file = st.file_uploader("📄 Upload Document", type=["pdf", "txt"])

# Question
question = st.text_input("❓ Ask a question about the document")

# Process
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

    # Safety check
    if len(content.strip()) < 50:
        st.warning("⚠️ Document is empty or too small.")
        st.stop()

    # 🔥 STRICT PROMPT
    prompt = f"""
You are a strict Legal Document Assistant.

Rules:
1. Answer ONLY using the provided document.
2. If the answer is NOT found in the document, say exactly:
   "The answer is not available in the provided document."
3. Do NOT use any external knowledge.
4. Always include a direct quote from the document as citation.

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

    # AI response
    with st.spinner("⚖️ Analyzing document..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
        except:
            # fallback model
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )

    answer = response.choices[0].message.content

    # 🔥 FINAL FILTER
    if "not available in the provided document" in answer.lower():
        st.error("❌ This question is not answered in the uploaded document.")
    else:
        st.success("✅ Answer based on document")
        st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)