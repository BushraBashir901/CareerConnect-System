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
    email = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
    
    skills_list = ["python", "django", "ml", "fastapi"]
    found_skills = [skill for skill in skills_list if skill.lower() in text.lower()]
    
    return {
        "email": email[0] if email else None,
        "skills": found_skills
    }