"""Restaurar a carteira de demonstração ao estado original (só ativo com IS_DEMO=true)."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from app import clock
from app.db import get_session
from scripts.seed_demo import reset as reset_demo_data

demo_bp = Blueprint("demo", __name__, url_prefix="/api/demo")


@demo_bp.post("/reset")
def reset():
    if not current_app.config["IS_DEMO"]:
        return jsonify(error="not_found"), 404
    reset_demo_data(get_session(), clock.today())
    return "", 204
