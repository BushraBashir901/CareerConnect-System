from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from app.models.job import Job
from app.models.user_resume import UserResume
from app.services.embeddings_service import generate_embedding


class JobSearchService:
    """
    Service for advanced job search using semantic similarity and filtering.
    """

    def __init__(self, db: Session):
        self.db = db

    def search_jobs_by_text(
        self,
        query: str,
        limit: int = 10,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:

        # 1. Generate query embedding
        query_embedding = generate_embedding(query)

        # 2. Personalization using resume embedding (optional)
        if user_id:
            user_resume = self.db.query(UserResume).filter(
                UserResume.user_id == user_id,
                UserResume.embedding.isnot(None)
            ).first()

            if user_resume and user_resume.embedding:
                resume_embedding = list(user_resume.embedding)

                query_embedding = [
                    0.7 * q + 0.3 * r
                    for q, r in zip(query_embedding, resume_embedding)
                ]

        # 3. Vector search query
        sql_query = text("""
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

        results = self.db.execute(sql_query, {
            "embedding": query_embedding,
            "limit": limit
        }).fetchall()

        # 4. Format response
        jobs = []
        for row in results:
            jobs.append({
                "job_id": row.job_id,
                "job_title": row.job_title,
                "job_description": row.job_description,
                "location": row.location,
                "salary_range": row.salary_range,
                "job_type": row.job_type,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "company_name": row.company_name,
                "company_description": row.company_description,
                "similarity_score": float(row.similarity_score)
            })

        return jobs

    def search_similar_jobs(self, job_id: int, limit: int = 5) -> List[Dict[str, Any]]:

        reference_job = self.db.query(Job).filter(Job.job_id == job_id).first()
        if not reference_job or not reference_job.embedding:
            return []

        embedding = list(reference_job.embedding)

        sql_query = text("""
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

        results = self.db.execute(sql_query, {
            "embedding": embedding,
            "job_id": job_id,
            "limit": limit
        }).fetchall()

        similar_jobs = []
        for row in results:
            similar_jobs.append({
                "job_id": row.job_id,
                "job_title": row.job_title,
                "job_description": row.job_description,
                "location": row.location,
                "salary_range": row.salary_range,
                "job_type": row.job_type,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "company_name": row.company_name,
                "company_description": row.company_description,
                "similarity_score": float(row.similarity_score)
            })

        return similar_jobs

    def get_jobs_by_location(self, location: str, limit: int = 20) -> List[Dict[str, Any]]:

        jobs = self.db.query(Job).join(Job.company).filter(
            and_(
                Job.is_active,
                or_(
                    Job.location.ilike(f"%{location}%"),
                    Job.location.ilike(f"%{location.title()}%")
                )
            )
        ).limit(limit).all()

        return [
            {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "job_description": job.job_description,
                "location": job.location,
                "salary_range": job.salary_range,
                "job_type": job.job_type,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "company_name": job.company.company_name if job.company else None,
                "company_description": job.company.company_description if job.company else None,
                "similarity_score": 1.0
            }
            for job in jobs
        ]

    def get_jobs_by_type(self, job_type: str, limit: int = 20) -> List[Dict[str, Any]]:

        jobs = self.db.query(Job).join(Job.company).filter(
            and_(
                Job.is_active,
                Job.job_type.ilike(f"%{job_type}%")
            )
        ).limit(limit).all()

        return [
            {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "job_description": job.job_description,
                "location": job.location,
                "salary_range": job.salary_range,
                "job_type": job.job_type,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "company_name": job.company.company_name if job.company else None,
                "company_description": job.company.company_description if job.company else None,
                "similarity_score": 1.0
            }
            for job in jobs
        ]