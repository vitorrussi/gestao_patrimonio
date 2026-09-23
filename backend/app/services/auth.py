from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.user import User

# Comparado quando o e-mail não existe, para o login levar o mesmo tempo nos dois casos.
_DUMMY_PASSWORD_HASH = generate_password_hash("senha-inexistente-para-timing")


class EmailAlreadyRegistered(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register_user(session: Session, email: str, password: str) -> User:
    email = normalize_email(email)
    if session.scalar(select(User.id).where(User.email == email)) is not None:
        raise EmailAlreadyRegistered(email)
    user = User(email=email, password_hash=generate_password_hash(password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        # Dois cadastros simultâneos do mesmo e-mail: a constraint única decide.
        session.rollback()
        raise EmailAlreadyRegistered(email) from exc
    return user


def authenticate(session: Session, email: str, password: str) -> User | None:
    user = session.scalar(select(User).where(User.email == normalize_email(email)))
    if user is None:
        check_password_hash(_DUMMY_PASSWORD_HASH, password)
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    return user
