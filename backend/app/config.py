from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent

load_dotenv(REPO_ROOT / ".env")

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    raise ValueError(f"{name} deve ser true ou false, recebido: {raw!r}")


class Config:
    """Configuração da aplicação, lida do ambiente com defaults seguros."""

    def __init__(self) -> None:
        self.data_dir = Path(os.environ.get("DATA_DIR", str(REPO_ROOT / "data")))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database_url = os.environ.get("DATABASE_URL", f"sqlite:///{self.data_dir / 'app.db'}")
        self.frontend_dist_dir = Path(
            os.environ.get("FRONTEND_DIST_DIR", str(REPO_ROOT / "frontend" / "dist"))
        )
        self.secret_key = os.environ.get("SECRET_KEY", "").strip()
        self.allow_registration = _env_bool("ALLOW_REGISTRATION", default=True)
        # Só true no container demo: habilita POST /api/demo/reset (veja app/routes/demo.py).
        self.is_demo = _env_bool("IS_DEMO", default=False)
