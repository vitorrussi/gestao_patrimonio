from __future__ import annotations

from typing import Any

from flask import request
from pydantic import BaseModel, ValidationError


class RequestValidationError(Exception):
    def __init__(self, details: list[dict[str, Any]]) -> None:
        super().__init__("dados inválidos")
        self.details = details


def parse_body[T: BaseModel](model: type[T]) -> T:
    """Valida o corpo JSON da requisição; erros viram 400 pelo handler do app."""
    payload = request.get_json(silent=True)
    if payload is None:
        raise RequestValidationError(
            [{"field": None, "type": "json_required", "message": "corpo JSON obrigatório"}]
        )
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise RequestValidationError(_error_details(exc)) from exc


def _error_details(exc: ValidationError) -> list[dict[str, Any]]:
    # Sem include_input: o valor enviado (ex.: a senha) nunca volta na resposta.
    return [
        {
            "field": ".".join(str(part) for part in error["loc"]) or None,
            "type": error["type"],
            "message": error["msg"],
        }
        for error in exc.errors(include_url=False, include_context=False, include_input=False)
    ]
