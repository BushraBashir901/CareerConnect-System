from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.user_resume import UserResume
from app.repositories.chatbot_repo.job_search_repo import JobSearchRepository
from app.services.embeddings_service import generate_embedding


class UserResumeRepository:
    """Small helper repo for resume data"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_resume(self, user_id: int):
        return self.db.query(UserResume).filter(
            UserResume.user_id == user_id,
            UserResume.embedding.isnot(None)
        ).first()


class JobSearchService:
    """
    Service: Business logic + AI + orchestration
    """

    def __init__(self, db: Session):
        self.repo = JobSearchRepository(db)
        self.resume_repo = UserResumeRepository(db)

    def search_jobs_by_text(
        self,
        query: str,
        limit: int = 10,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:

        query_embedding = generate_embedding(query)

        if user_id:
            user_resume = self.resume_repo.get_user_resume(user_id)

            if user_resume:
                resume_embedding = list(user_resume.embedding)

                query_embedding = [
                    0.7 * q + 0.3 * r
                    for q, r in zip(query_embedding, resume_embedding)
                ]

        results = self.repo.search_jobs_by_embedding(query_embedding, limit)

        return self._format_jobs(results)

   
    def search_similar_jobs(self, job_id: int, limit: int = 5):

        
        job = self.resume_repo.db.query(UserResume).filter(
            UserResume.job_id == job_id
        ).first()

        if not job or not job.embedding:
            return []

        results = self.repo.get_similar_jobs(
            list(job.embedding),
            job_id,
            limit
        )

        return self._format_jobs(results)

    def get_jobs_by_location(self, location: str, limit: int = 20):

        results = self.repo.get_by_location(location, limit)
        return self._format_jobs(results, similarity_fixed=True)

    def get_jobs_by_type(self, job_type: str, limit: int = 20):

        results = self.repo.get_by_type(job_type, limit)
        return self._format_jobs(results, similarity_fixed=True)

  
    def _format_jobs(self, results, similarity_fixed: bool = False):

        return [
            {
                "job_id": r.job_id,
                "job_title": r.job_title,
                "job_description": r.job_description,
                "location": r.location,
                "salary_range": r.salary_range,
                "job_type": r.job_type,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "company_name": r.company_name,
                "company_description": r.company_description,
                "similarity_score": float(
                    getattr(
                        r,
                        "similarity_score",
                        1.0 if similarity_fixed else 0.0
                    )
                )
            }
            for r in results
        ]