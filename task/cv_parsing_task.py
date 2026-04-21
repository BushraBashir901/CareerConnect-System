from app.utils.parser import extract_text, parse_data
from celery_worker import celery_app


@celery_app.task(name="parse_cv_resume")
def parse_cv_resume(file_path: str):
    """
    Simple CV parsing task for beginners.
    
    Args:
        file_path (str): Path to the uploaded file
    
    Returns:
        dict: Simple parsing result
    """
    try:
        # Extract text from file
        text = extract_text(file_path)
        print(f"Extracted text: {text}")
        
        if not text:
            return {"error": "Could not extract text"}
        
        # Parse the text for basic info
        parsed_data = parse_data(text)
        print(f"Parsed data: {parsed_data}")
        
        return {
            "success": True,
            "email": parsed_data.get("email"),
            "skills": parsed_data.get("skills"),
            "message": "CV parsed successfully"
        }
        
    except Exception as e:
        print(f"Error parsing CV: {e}")
        return {
            "success": False,
            "error": str(e)
        }
