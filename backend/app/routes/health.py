from __future__ import annotations

from flask import Blueprint, jsonify
from sqlalchemy import select

from app.db import get_session
from app.models.app_meta import AppMeta

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def get_health():
    session = get_session()
    row = session.scalar(select(AppMeta).where(AppMeta.chave == "status"))
    return jsonify(status="ok", database=row.valor if row is not None else None)
