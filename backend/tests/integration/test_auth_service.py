import pytest
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from app.models import User
from app.services.auth import EmailAlreadyRegistered, authenticate, register_user
from tests.constants import USER_EMAIL, USER_PASSWORD


def test_register_stores_hash_not_plain_password(db_session: Session) -> None:
    user = register_user(db_session, "novo@example.com", "minha-senha-1")

    assert user.id is not None
    assert user.password_hash != "minha-senha-1"
    assert "minha-senha-1" not in user.password_hash
    assert check_password_hash(user.password_hash, "minha-senha-1")


def test_register_normalizes_email(db_session: Session) -> None:
    user = register_user(db_session, "  Novo@Example.COM ", "minha-senha-1")

    assert user.email == "novo@example.com"


def test_register_rejects_duplicate_email_ignoring_case(db_session: Session, user: User) -> None:
    with pytest.raises(EmailAlreadyRegistered):
        register_user(db_session, USER_EMAIL.upper(), "outra-senha-123")


def test_authenticate_with_correct_password_returns_user(db_session: Session, user: User) -> None:
    assert authenticate(db_session, USER_EMAIL, USER_PASSWORD) == user


def test_authenticate_ignores_email_case(db_session: Session, user: User) -> None:
    assert authenticate(db_session, USER_EMAIL.upper(), USER_PASSWORD) == user


def test_authenticate_with_wrong_password_returns_none(db_session: Session, user: User) -> None:
    assert authenticate(db_session, USER_EMAIL, "senha-errada-123") is None


def test_authenticate_with_unknown_email_returns_none(db_session: Session) -> None:
    assert authenticate(db_session, "ninguem@example.com", USER_PASSWORD) is None
