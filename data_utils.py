import io
from pypdf import PdfReader
import docx

def extract_text_from_pdf(uploaded_file):
    """Extract text content from a PDF file using pypdf."""
    text = ""
    
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return {"Content": [text]}  

def extract_text_from_doc(uploaded_file):
    """Extract text from DOCX using python-docx."""
    text = ""
    doc = docx.Document(io.BytesIO(uploaded_file.read()))
    for para in doc.paragraphs:
        text += para.text + "\n"
    return {"Content": [text]}
