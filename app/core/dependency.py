from app.db.session import SessionLocal

def get_db():
    """
    FastAPI dependency to get a database session.
    Usage: def endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()