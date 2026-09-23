from __future__ import annotations

from flask import Flask, abort, jsonify, request
from flask_login import LoginManager, current_user

from app.db import get_session
from app.models.user import User

# Únicas rotas /api acessíveis sem login. Qualquer outra rota /api nasce protegida.
PUBLIC_API_ENDPOINTS = frozenset({"health.get_health", "auth.register", "auth.login"})

login_manager = LoginManager()


@login_manager.user_loader
def _load_user(user_id: str) -> User | None:
    return get_session().get(User, int(user_id))


@login_manager.unauthorized_handler
def _unauthorized():
    return jsonify(error="unauthorized"), 401


def get_current_user() -> User:
    """Usuário logado, tipado. Use para filtrar dados pelo dono (regra 2)."""
    user = current_user._get_current_object()
    if not isinstance(user, User):
        abort(401)
    return user


def is_api_path(path: str) -> bool:
    return path == "/api" or path.startswith("/api/")


def _require_login():
    if not is_api_path(request.path) or request.endpoint in PUBLIC_API_ENDPOINTS:
        return None
    if current_user.is_authenticated:
        return None
    return jsonify(error="unauthorized"), 401


def init_auth(app: Flask) -> None:
    login_manager.init_app(app)
    app.before_request(_require_login)
