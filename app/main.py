from document_processor import extract_text_from_pdf
from ai_workflow import summarize_document

pdf_path = "data/uploads/sample.pdf"
text = extract_text_from_pdf(pdf_path)
summary = summarize_document(text)
print(summary)
