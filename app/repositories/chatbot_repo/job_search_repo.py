from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from app.models.job import Job


class JobSearchRepository:
    """
    Repository: ONLY database operations (SQL / ORM)
    """

    def __init__(self, db: Session):
        self.db = db

    def search_jobs_by_embedding(self, embedding, limit: int = 10):

        sql = text("""
            SELECT 
                j.*,
                c.company_name,
                c.company_description,
                1 - (j.embedding <=> CAST(:embedding AS vector)) as similarity_score
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.embedding IS NOT NULL 
            AND j.is_active = true
            ORDER BY j.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)

        return self.db.execute(sql, {
            "embedding": embedding,
            "limit": limit
        }).fetchall()

   
    def get_similar_jobs(self, embedding, job_id: int, limit: int = 5):

        sql = text("""
            SELECT 
                j.*,
                c.company_name,
                c.company_description,
                1 - (j.embedding <=> CAST(:embedding AS vector)) as similarity_score
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.embedding IS NOT NULL 
            AND j.is_active = true
            AND j.job_id != :job_id
            ORDER BY j.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)

        return self.db.execute(sql, {
            "embedding": embedding,
            "job_id": job_id,
            "limit": limit
        }).fetchall()

   
    def get_by_location(self, location: str, limit: int):

        return self.db.query(Job).join(Job.company).filter(
            and_(
                Job.is_active,
                or_(
                    Job.location.ilike(f"%{location}%"),
                    Job.location.ilike(f"%{location.title()}%")
                )
            )
        ).limit(limit).all()

   
    def get_by_type(self, job_type: str, limit: int):

        return self.db.query(Job).join(Job.company).filter(
            and_(
                Job.is_active,
                Job.job_type.ilike(f"%{job_type}%")
            )
        ).limit(limit).all()