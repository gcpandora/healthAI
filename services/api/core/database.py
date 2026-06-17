"""
HealthAI Coach — Database Configuration
Initialisation SQLAlchemy, SessionLocal et déclaration de la Base
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

from .config import settings


engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,  
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI : fournit une session DB pour chaque request.
    Utilisage: async def my_endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
