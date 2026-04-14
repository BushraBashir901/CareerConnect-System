from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str  # e.g., postgresql+psycopg2://user:pass@localhost/dbname
    

    class Config:
        env_file = ".env"

settings = Settings()