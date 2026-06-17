import os

# Doit être positionné avant tout import de core.database
# pour que create_engine() utilise SQLite (pas PostgreSQL/psycopg2)
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
