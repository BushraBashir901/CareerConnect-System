from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from app.models.job import Job
from app.models.user_resume import UserResume
from app.services.embeddings_service import generate_embedding

class JobSearchService:
    """
    Service for advanced job search using semantic similarity and filtering.
    
    Provides intelligent job matching using vector embeddings, personalized search
    based on user resumes, and various filtering options for optimal job discovery.
    
    Attributes:
        db: Database session for data persistence and queries
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_jobs_by_text(self, query: str, limit: int = 10, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search jobs using semantic similarity with the query text.
        
        Args:
            query: The search query (job description, skills, etc.)
            limit: Maximum number of results to return
            user_id: Optional user ID to personalize search based on their resume
            
        Returns:
            List of job dictionaries with similarity scores
        """
        # Generate embedding for the search query
        query_embedding = generate_embedding(query)
        
        # If user_id is provided, try to incorporate their resume embedding for better matching
        if user_id:
            user_resume = self.db.query(UserResume).filter(
                UserResume.user_id == user_id,
                UserResume.embedding.isnot(None)
            ).first()
            
            if user_resume and user_resume.embedding:
                # Combine query embedding with user resume embedding for personalized search
                resume_embedding = list(user_resume.embedding)
                # Weight the query more heavily (70%) and resume less (30%)
                combined_embedding = [
                    0.7 * q + 0.3 * r 
                    for q, r in zip(query_embedding, resume_embedding)
                ]
                query_embedding = combined_embedding
        
        # Convert embedding to string for PostgreSQL vector operations
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Perform similarity search using pgvector
        sql_query = text(f"""
            SELECT 
                j.*,
                c.company_name,
                c.company_description,
                1 - (j.embedding <=> {embedding_str}) as similarity_score
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.embedding IS NOT NULL 
            AND j.is_active = true
            ORDER BY j.embedding <=> {embedding_str}
            LIMIT :limit
        """)
        
        results = self.db.execute(sql_query, {"limit": limit}).fetchall()
        
        # Convert results to list of dictionaries
        jobs = []
        for row in results:
            job_dict = {
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
            }
            jobs.append(job_dict)
        
        return jobs
    
    def search_similar_jobs(self, job_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find jobs similar to a specific job.
        
        Args:
            job_id: ID of the reference job
            limit: Maximum number of similar jobs to return
            
        Returns:
            List of similar job dictionaries
        """
        # Get the reference job and its embedding
        reference_job = self.db.query(Job).filter(Job.job_id == job_id).first()
        if not reference_job or not reference_job.embedding:
            return []
        
        # Convert embedding to string for PostgreSQL vector operations
        embedding_str = f"[{','.join(map(str, list(reference_job.embedding)))}]"
        
        # Find similar jobs (excluding the reference job itself)
        sql_query = text(f"""
            SELECT 
                j.*,
                c.company_name,
                c.company_description,
                1 - (j.embedding <=> {embedding_str}) as similarity_score
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.embedding IS NOT NULL 
            AND j.is_active = true
            AND j.job_id != :job_id
            ORDER BY j.embedding <=> {embedding_str}
            LIMIT :limit
        """)
        
        results = self.db.execute(sql_query, {"job_id": job_id, "limit": limit}).fetchall()
        
        # Convert results to list of dictionaries
        similar_jobs = []
        for row in results:
            job_dict = {
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
            }
            similar_jobs.append(job_dict)
        
        return similar_jobs
    
    def get_jobs_by_location(self, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get jobs filtered by location (text-based search).
        
        Args:
            location: Location to search for
            limit: Maximum number of results
            
        Returns:
            List of job dictionaries
        """
        jobs = self.db.query(Job).join(Job.company).filter(
            and_(
                Job.is_active,
                or_(
                    Job.location.ilike(f"%{location}%"),
                    Job.location.ilike(f"%{location.title()}%")
                )
            )
        ).limit(limit).all()
        
        job_list = []
        for job in jobs:
            job_dict = {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "job_description": job.job_description,
                "location": job.location,
                "salary_range": job.salary_range,
                "job_type": job.job_type,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "company_name": job.company.company_name if job.company else None,
                "company_description": job.company.company_description if job.company else None,
                "similarity_score": 1.0  # Perfect match for location-based search
            }
            job_list.append(job_dict)
        
        return job_list
    
    def get_jobs_by_type(self, job_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get jobs filtered by job type.
        
        Args:
            job_type: Type of job (full-time, part-time, contract, etc.)
            limit: Maximum number of results
            
        Returns:
            List of job dictionaries
        """
        jobs = self.db.query(Job).join(Job.company).filter(
            and_(
                Job.is_active,
                Job.job_type.ilike(f"%{job_type}%")
            )
        ).limit(limit).all()
        
        job_list = []
        for job in jobs:
            job_dict = {
                "job_id": job.job_id,
                "job_title": job.job_title,
                "job_description": job.job_description,
                "location": job.location,
                "salary_range": job.salary_range,
                "job_type": job.job_type,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "company_name": job.company.company_name if job.company else None,
                "company_description": job.company.company_description if job.company else None,
                "similarity_score": 1.0  # Perfect match for type-based search
            }
            job_list.append(job_dict)
        
        return job_list
