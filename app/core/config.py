from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore" 
    }

    # Database
    DATABASE_URL: str
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    BACKEND_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_BROKER_URL: str = "redis://localhost:6379/0"
    REDIS_BACKEND_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    # Email settings
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    APP_BASE_URL: str

settings = Settings()