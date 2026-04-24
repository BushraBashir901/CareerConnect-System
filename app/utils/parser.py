from pypdf import PdfReader
from docx import Document
import re


# from pypdf import PdfReader
# try:
#     from docx import Document
# except ImportError:
#     Document = None
# import re


def extract_text(file_path: str) -> str:
    """
    Extract text content from PDF and DOCX files.
    
    Supports PDF files using pypdf and DOCX files using python-docx.
    Returns empty string for unsupported file formats.
    
    Args:
        file_path: Path to the file to extract text from
        
    Returns:
        str: Extracted text content, or empty string if extraction fails
        
    Note:
        - PDF: Extracts text from all pages
        - DOCX: Extracts text from all paragraphs
        - Other formats: Returns empty string
    """
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif file_path.endswith(".docx"):
        if Document:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return ""

    else:
        return ""
    
def parse_data(text):
    """
    Parse resume text to extract email and skills information.
    
    Uses regex patterns to find email addresses and searches for
    predefined skills in the text.
    
    Args:
        text: Resume text content to parse
        
    Returns:
        dict: Dictionary containing:
            - email: First found email address or None
            - skills: List of found skills from predefined list
            
    Note:
        Currently searches for: python, django, ml, fastapi
        Skills matching is case-insensitive
    """
    email = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
    
    skills_list = ["python", "django", "ml", "fastapi"]
    found_skills = [skill for skill in skills_list if skill.lower() in text.lower()]
    
    return {
        "email": email[0] if email else None,
        "skills": found_skills
    }