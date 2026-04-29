from openai import OpenAI
from app.core.config import settings

# Single reusable OpenAI client for the entire application
client = OpenAI(api_key=settings.OPENAI_API_KEY)