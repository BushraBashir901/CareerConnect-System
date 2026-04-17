from fastapi import UploadFile


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file:UploadFile)-> bool:
    filename=file.filename.split('.')[-1].lower()
    if filename not in ALLOWED_EXTENSIONS:
        return False
    if file.size > MAX_FILE_SIZE:
        return False
    return True