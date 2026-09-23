import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest
from app.services.auth import normalize_email


def test_normalize_email_strips_and_lowercases() -> None:
    assert normalize_email("  Dono@Example.COM ") == "dono@example.com"


def test_register_request_normalizes_email() -> None:
    data = RegisterRequest.model_validate({"email": " A@B.com ", "password": "12345678"})

    assert data.email == "a@b.com"


@pytest.mark.parametrize("email", ["", "sem-arroba", "a@b", "a b@c.com", "a@@b.com", "@b.com"])
def test_register_request_rejects_malformed_email(email: str) -> None:
    with pytest.raises(ValidationError):
        RegisterRequest.model_validate({"email": email, "password": "12345678"})


@pytest.mark.parametrize("password", ["1234567", "x" * 129])
def test_register_request_rejects_password_outside_length_limits(password: str) -> None:
    with pytest.raises(ValidationError):
        RegisterRequest.model_validate({"email": "a@b.com", "password": password})


@pytest.mark.parametrize("password", ["12345678", "x" * 128])
def test_register_request_accepts_password_at_length_limits(password: str) -> None:
    data = RegisterRequest.model_validate({"email": "a@b.com", "password": password})

    assert data.password == password


def test_register_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest.model_validate({"email": "a@b.com", "password": "12345678", "admin": True})
