from app.utils.parser import extract_text, parse_data
from celery_worker import celery_app
from app.services.embeddings_service import generate_embedding
from app.models.user_resume import UserResume
from app.db.session import SessionLocal


@celery_app.task(name="parse_cv_resume")
def parse_cv_resume(file_path: str, user_id: int):
    """
    Parse CV and save data to database.

    Args:
        file_path (str): Path to the uploaded file
        user_id (int): ID of the user who owns the resume

    Returns:
        dict: Parsing result with resume ID
    """
    print(f"Starting CV parsing for file: {file_path}, user: {user_id}")
    db = SessionLocal()
    try:
        # Extract text from file
        print(f"Extracting text from file: {file_path}")
        text = extract_text(file_path)
        print(f"Extracted text length: {len(text) if text else 0}")
        print(f"Extracted text preview: {text[:200] if text else 'No text'}")

        if not text:
            print("No text extracted from file")
            return {"error": "Could not extract text"}

        # Generate embedding
        print("Generating embedding...")
        embedding = generate_embedding(text)
        print(f"Embedding generated: {len(embedding)} dimensions")

        # Parse the text for basic info
        print("Parsing data...")
        parsed_data = parse_data(text)
        print(f"Parsed data: {parsed_data}")

        # Create UserResume record
        print("Creating UserResume record...")
        resume = UserResume(
            user_id=user_id,
            raw_text=text,  # Store extracted text as raw_text
            clear_text={
                "parsed_content": text,
                "structured_data": parsed_data,
            },  # Store as JSONB
            file_path=file_path,
            filename=file_path.split("/")[-1],  # Extract filename from path
            embedding=embedding,
        )
        print("UserResume record created")

        # Save to database
        print("Adding to database...")
        db.add(resume)
        print("Committing to database...")
        db.commit()
        print("Refreshing record...")
        db.refresh(resume)
        print(f"Record saved with ID: {resume.user_resume_id}")

        return {
            "success": True,
            "resume_id": resume.user_resume_id,
            "email": parsed_data.get("email"),
            "skills": parsed_data.get("skills"),
            "message": "CV parsed and saved successfully",
        }

    except Exception as e:
        print(f"Error parsing CV: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()
        print("Database connection closed")
