from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify
from flask_login import login_user, logout_user

from app.auth import get_current_user
from app.db import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services.auth import EmailAlreadyRegistered, authenticate, register_user
from app.validation import parse_body

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _user_json(user: User) -> Response:
    data = UserResponse(id=user.id, email=user.email, is_demo=current_app.config["IS_DEMO"])
    return jsonify(data.model_dump())


@auth_bp.post("/register")
def register():
    if not current_app.config["ALLOW_REGISTRATION"]:
        return jsonify(error="registration_disabled"), 403
    data = parse_body(RegisterRequest)
    try:
        user = register_user(get_session(), data.email, data.password)
    except EmailAlreadyRegistered:
        return jsonify(error="email_already_registered"), 409
    login_user(user)
    return _user_json(user), 201


@auth_bp.post("/login")
def login():
    data = parse_body(LoginRequest)
    user = authenticate(get_session(), data.email, data.password)
    if user is None:
        return jsonify(error="invalid_credentials", message="E-mail ou senha inválidos"), 401
    login_user(user)
    return _user_json(user)


@auth_bp.post("/logout")
def logout():
    logout_user()
    return "", 204


@auth_bp.get("/me")
def me():
    return _user_json(get_current_user())
