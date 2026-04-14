from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base

# Define the database URL (replace with your actual database credentials)

DATABASE_URL= "postgresql+psycopg2://postgres:21Jan2003%40@localhost:5432/careerconnect"


# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL,pool_pre_ping=True)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


