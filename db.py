"""
db.py - SQLAlchemy engine/session management and init helper.

Usage:
- init_db(database_url)  # creates tables if not present (via SQLAlchemy metadata.create_all)
- get_session() -> Session
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from models import Base

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


def init_db(database_url: str = None):
    """
    Initialize engine & session factory and create tables.
    If database_url is None, read from env SQLALCHEMY_DATABASE_URI.
    """
    global _engine, _SessionLocal
    url = database_url or os.environ.get("SQLALCHEMY_DATABASE_URI") or os.environ.get(
        "DATABASE_URL"
    )
    if not url:
        raise RuntimeError("Database URL not provided (SQLALCHEMY_DATABASE_URI or DATABASE_URL)")

    if _engine is None:
        # echo can be turned on via env for debugging
        _engine = create_engine(url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        logger.info("SQLAlchemy engine created for %s", url)

    # create tables if not exist (safe)
    try:
        Base.metadata.create_all(bind=_engine)
        logger.info("Tables ensured via SQLAlchemy metadata.create_all()")
    except SQLAlchemyError:
        logger.exception("Failed to create tables")
        raise


def get_session():
    """
    Return a new SQLAlchemy Session. Caller should close() it.
    """
    global _SessionLocal
    if _SessionLocal is None:
        # attempt to initialize from env
        init_db()
    return _SessionLocal()
