import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


class TestAuthFlow:
    def test_register_new_user(self, client):
        response = client.post(
            "/auth/register",
            json={"username": "newuser", "password": "password123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "user_key" in data
        assert "hashed_password" not in data

    def test_register_duplicate_user(self, client):
        client.post(
            "/auth/register",
            json={"username": "duplicate", "password": "password123"}
        )

        response = client.post(
            "/auth/register",
            json={"username": "duplicate", "password": "password123"}
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_with_correct_credentials(self, client):
        client.post(
            "/auth/register",
            json={"username": "loginuser", "password": "password123"}
        )

        response = client.post(
            "/auth/login",
            json={"username": "loginuser", "password": "password123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_wrong_password(self, client):
        client.post(
            "/auth/register",
            json={"username": "wrongpw", "password": "correctpassword"}
        )

        response = client.post(
            "/auth/login",
            json={"username": "wrongpw", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_with_nonexistent_user(self, client):
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )

        assert response.status_code == 401

    def test_access_protected_endpoint_without_token(self, client):
        response = client.post(
            "/chat",
            json={"message": "Hello"}
        )

        assert response.status_code == 403

    def test_access_protected_endpoint_with_invalid_token(self, client):
        response = client.post(
            "/chat",
            headers={"Authorization": "Bearer invalid_token"},
            json={"message": "Hello"}
        )

        assert response.status_code == 401

    def test_full_auth_flow_register_login_access(self, client):
        register_response = client.post(
            "/auth/register",
            json={"username": "flowuser", "password": "password123"}
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/auth/login",
            json={"username": "flowuser", "password": "password123"}
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        protected_response = client.post(
            "/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Test message"}
        )

        assert protected_response.status_code in [200, 500]
