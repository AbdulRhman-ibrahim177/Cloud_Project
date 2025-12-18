from datetime import datetime
from pathlib import Path

import yaml
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker

# Load config
CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

DATABASE_URL = config["database"]["url"]

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)

    # Cloud storage info
    s3_key = Column(String, nullable=True)
    notes_path = Column(String, nullable=True)  # local path للـ notes (أو ممكن تعمل s3_notes_key)

    status = Column(String, default="uploaded")  # uploaded / processed / failed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
