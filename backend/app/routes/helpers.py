from __future__ import annotations

from collections.abc import Iterable

from flask import Response, abort, jsonify

from app.auth import get_current_user


def current_user_id() -> int:
    return get_current_user().id


def require[T](obj: T | None) -> T:
    """404 quando o registro não existe ou é de outro usuário (não revela qual dos dois)."""
    if obj is None:
        abort(404)
    return obj


def rule_locked_response(fields: Iterable[str]) -> tuple[Response, int]:
    return jsonify(
        error="rule_locked_by_payments",
        fields=sorted(fields),
        message=(
            "Já existem pagamentos para esta regra. Para mudar datas ou periodicidade, "
            "encerre a atual (data de fim ou quitado) e cadastre uma nova."
        ),
    ), 409


def no_content() -> tuple[str, int]:
    return "", 204
