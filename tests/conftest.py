import pytest
from app.main import app
from fastapi.testclient import TestClient
from app.database import db
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    yield
    # Nettoyage après chaque test
    with db.get_session() as session:
        session.run("MATCH (n) WHERE n.id STARTS WITH 'test_' DETACH DELETE n")