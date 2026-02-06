import pytest
from datetime import timedelta
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password
)


class TestPasswordHashing:
    def test_hash_password_returns_different_hash_for_same_password(self):
        password = "test123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert hash1.startswith("$2b$")

    def test_verify_password_with_correct_password(self):
        password = "test123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_wrong_password(self):
        password = "test123"
        wrong_password = "wrong123"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_password_handles_special_characters(self):
        password = "P@ssw0rd!#$%"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True


class TestJWTTokens:
    def test_create_access_token_default_expiration(self):
        data = {"sub": "123"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_custom_expiration(self):
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)

        assert isinstance(token, str)

    def test_decode_access_token_valid(self):
        data = {"sub": "123", "username": "test"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["username"] == "test"
        assert "exp" in decoded
        assert "iat" in decoded
        assert decoded["type"] == "access"

    def test_decode_access_token_invalid(self):
        invalid_token = "invalid.token.here"

        decoded = decode_access_token(invalid_token)

        assert decoded is None

    def test_decode_access_token_expired(self):
        data = {"sub": "123"}
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)

        decoded = decode_access_token(token)

        assert decoded is None

    def test_token_contains_required_fields(self):
        data = {"sub": "456"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert "sub" in decoded
        assert "exp" in decoded
        assert "iat" in decoded
        assert "type" in decoded
