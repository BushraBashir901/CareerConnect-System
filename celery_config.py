from celery import Celery
import os
import dotenv

dotenv.load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery(
    'careerconnect_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
    )

#configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)