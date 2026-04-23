
from celery import Celery
from app.core.config import settings

# Redis configuration
broker = settings.REDIS_BROKER_URL
backend = settings.REDIS_BACKEND_URL

# Create Celery app
celery_app = Celery(
    'careerconnect_tasks',
    broker=broker,
    backend=backend
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Windows-specific settings
    worker_pool='solo',  # Use solo pool for Windows
    worker_concurrency=1,  # Single worker for Windows
    
    
)

# Import task modules directly to register them
from task import cv_parsing_task
from task import send_email_invitation_task

print("Task modules imported and registered!")

if __name__ == '__main__':
    # Start celery_worker
    celery_app.start()
