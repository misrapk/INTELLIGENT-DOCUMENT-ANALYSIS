import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.document_processor import extract_text_from_pdf
from app.document_processor import extract_text_from_pdf
from app.ai_workflow import summarize_document

st.title("Intelligent Document Analyzer (Perplexity API)")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file:
    file_path = f"data/uploads/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    st.info("Extracting text...")
    text = extract_text_from_pdf(file_path)
    st.success("Text extracted! Sending to Perplexity API...")
    summary = summarize_document(text)
    st.subheader("Document Summary and Insights")
    st.write(summary)
