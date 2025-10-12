import sys
import subprocess
import streamlit as st

st.write("Python executable:", sys.executable)

try:
    import pdfplumber
    st.write("pdfplumber is installed")
except ImportError:
    st.write("pdfplumber is NOT installed")