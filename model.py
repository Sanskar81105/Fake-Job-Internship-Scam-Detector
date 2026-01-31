"""
models.py - SQLAlchemy models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_description = Column(Text, nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(10), nullable=False)
    reasons = Column(JSON, nullable=False)  # requires MySQL 5.7+; SQLAlchemy will handle fallback in SQLite tests
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
