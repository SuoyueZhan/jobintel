import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://jobintel:jobintel_pw@localhost:5432/jobintel",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency that yields a DB session per request.

    Why 'yield':
    - code before yield runs to create the session
    - code after yield runs no matter what (finally), so we can close cleanly
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
