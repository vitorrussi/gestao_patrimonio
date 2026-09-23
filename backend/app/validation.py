from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import request
from pydantic import BaseModel, ValidationError


class RequestValidationError(Exception):
    def __init__(self, details: list[dict[str, Any]]) -> None:
        super().__init__("dados inválidos")
        self.details = details


def _single_error(error_type: str, message: str) -> RequestValidationError:
    return RequestValidationError([{"field": None, "type": error_type, "message": message}])


def _validate[T: BaseModel](model: type[T], data: object) -> T:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise RequestValidationError(_error_details(exc)) from exc


def _json_object() -> dict[str, Any]:
    payload = request.get_json(silent=True)
    if payload is None:
        raise _single_error("json_required", "corpo JSON obrigatório")
    if not isinstance(payload, dict):
        raise _single_error("json_object_required", "o corpo JSON deve ser um objeto")
    return payload


def parse_body[T: BaseModel](model: type[T]) -> T:
    """Valida o corpo JSON da requisição; erros viram 400 pelo handler do app."""
    payload = request.get_json(silent=True)
    if payload is None:
        raise _single_error("json_required", "corpo JSON obrigatório")
    return _validate(model, payload)


@dataclass(frozen=True)
class Patch[T: BaseModel]:
    old: T
    new: T
    changed: frozenset[str]


def parse_patch[T: BaseModel](model: type[T], current: dict[str, Any]) -> Patch[T]:
    """PATCH: só os campos enviados mudam; o resultado é validado inteiro (regras entre campos)."""
    payload = _json_object()
    old = _validate(model, current)
    new = _validate(model, current | payload)
    changed = frozenset(
        name for name in model.model_fields if getattr(old, name) != getattr(new, name)
    )
    return Patch(old=old, new=new, changed=changed)


def parse_query[T: BaseModel](model: type[T]) -> T:
    return _validate(model, request.args.to_dict())


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
