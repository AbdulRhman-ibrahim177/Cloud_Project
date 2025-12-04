"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import yaml
from pathlib import Path

from models import Base

# Load config
CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Get database config
DB_HOST = os.getenv("DB_HOST", config["database"]["host"])
DB_PORT = os.getenv("DB_PORT", config["database"]["port"])
DB_NAME = os.getenv("DB_NAME", config["database"]["name"])
DB_USER = os.getenv("DB_USER", config["database"]["user"])
DB_PASSWORD = os.getenv("DB_PASSWORD", config["database"]["password"])

# Handle ${VAR} syntax in config
if isinstance(DB_HOST, str) and DB_HOST.startswith("${"):
    DB_HOST = os.getenv(DB_HOST.strip("${}").split(":-")[0], "localhost")
if isinstance(DB_PORT, str) and str(DB_PORT).startswith("${"):
    DB_PORT = os.getenv(str(DB_PORT).strip("${}").split(":-")[0], "5432")
if isinstance(DB_NAME, str) and DB_NAME.startswith("${"):
    DB_NAME = os.getenv(DB_NAME.strip("${}").split(":-")[0], "quiz_service")
if isinstance(DB_USER, str) and DB_USER.startswith("${"):
    DB_USER = os.getenv(DB_USER.strip("${}").split(":-")[0], "postgres")
if isinstance(DB_PASSWORD, str) and DB_PASSWORD.startswith("${"):
    DB_PASSWORD = os.getenv(DB_PASSWORD.strip("${}").split(":-")[0], "postgres")

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("[Database] Tables created successfully")


@contextmanager
def get_db() -> Session:
    """Get database session as context manager"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session():
    """Get database session (for FastAPI dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
