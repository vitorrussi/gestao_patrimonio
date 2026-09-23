from __future__ import annotations

from pathlib import Path

from flask import Flask, g, jsonify, request, send_from_directory

from app.config import Config
from app.db import create_engine_with_pragmas, make_session_factory
from app.routes.health import health_bp


def create_app(config: Config | None = None) -> Flask:
    config = config or Config()
    app = Flask(__name__, static_folder=None)
    app.config["APP_CONFIG"] = config

    engine = create_engine_with_pragmas(config.database_url)
    app.extensions["db_engine"] = engine
    app.extensions["db_session_factory"] = make_session_factory(engine)

    app.register_blueprint(health_bp)
    _register_frontend_routes(app, config.frontend_dist_dir)

    @app.teardown_appcontext
    def _close_db_session(exception: BaseException | None) -> None:
        session = g.pop("db_session", None)
        if session is not None:
            session.close()

    return app


def _register_frontend_routes(app: Flask, dist_dir: Path) -> None:
    def _index_response():
        if not (dist_dir / "index.html").is_file():
            return (
                "Frontend não buildado. Rode 'npm run dev' em frontend/ "
                "para desenvolvimento, ou 'docker compose up --build'.",
                200,
            )
        return send_from_directory(dist_dir, "index.html")

    @app.errorhandler(404)
    def _handle_not_found(error: object):
        if request.path.startswith("/api/"):
            return jsonify(error="not_found"), 404
        return _index_response()

    @app.get("/")
    @app.get("/<path:path>")
    def _serve_frontend(path: str = ""):
        target = dist_dir / path
        if path and target.is_file():
            return send_from_directory(dist_dir, path)
        return _index_response()
