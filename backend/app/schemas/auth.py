from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.auth import normalize_email

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=254)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = normalize_email(value)
        if not EMAIL_PATTERN.match(email):
            raise ValueError("e-mail inválido")
        return email


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
