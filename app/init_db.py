from app.db import engine
from app.models import Base

def init_db() -> None:
    # Create tables for all models if they don't exist
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("DB schema ensured.")
