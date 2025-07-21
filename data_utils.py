import pdfplumber
import docx
import io
def extract_text_from_pdf(uploaded_file):
    """Extract text content from a PDF file using pdfplumber."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return {"Content": [text]}  # Return as dict so we can convert to DataFrame


def extract_text_from_doc(uploaded_file):
    """Extract text from DOCX or DOC using python-docx."""
    text = ""
    doc = docx.Document(uploaded_file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return {"Content": [text]}  # Return as dict so we can convert to DataFrame
