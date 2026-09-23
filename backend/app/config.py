from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent

load_dotenv(REPO_ROOT / ".env")


class Config:
    """Configuração da aplicação, lida do ambiente com defaults seguros."""

    def __init__(self) -> None:
        self.data_dir = Path(os.environ.get("DATA_DIR", str(REPO_ROOT / "data")))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database_url = os.environ.get(
            "DATABASE_URL", f"sqlite:///{self.data_dir / 'app.db'}"
        )
        self.frontend_dist_dir = Path(
            os.environ.get(
                "FRONTEND_DIST_DIR", str(REPO_ROOT / "frontend" / "dist")
            )
        )
