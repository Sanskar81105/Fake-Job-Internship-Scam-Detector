import json
import pytest
from server import create_app
from db import init_db
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def app():
    # Use an in-memory SQLite DB for tests
    test_db_url = "sqlite:///:memory:"
    test_config = {"SQLALCHEMY_DATABASE_URI": test_db_url, "TESTING": True}
    app = create_app(test_config=test_config)
    # Ensure tables exist
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"

def test_analyze_job_and_persist(client):
    desc = "Immediate hire. No interview. Pay registration fee. Contact WhatsApp only."
    resp = client.post("/analyze-job", json={"job_description": desc})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "risk_score" in data
    assert "reasons" in data
    # persisted may be True for SQLAlchemy SQLite test; ensure response contains persisted key
    assert "persisted" in data

def test_analyses_listing(client):
    # Create a few entries
    for i in range(3):
        desc = f"Test job {i} registration fee"
        client.post("/analyze-job", json={"job_description": desc})
    resp = client.get("/analyses")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total" in data
    assert data["total"] >= 3
    assert "items" in data
    assert isinstance(data["items"], list)
