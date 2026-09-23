from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, g, jsonify, request, send_from_directory

from app.auth import init_auth, is_api_path
from app.config import Config
from app.db import create_engine_with_pragmas, make_session_factory
from app.routes.auth import auth_bp
from app.routes.demo import demo_bp
from app.routes.health import health_bp
from app.routes.payments import payments_bp
from app.routes.properties import properties_bp
from app.routes.records import records_bp
from app.routes.views import views_bp
from app.validation import RequestValidationError

MISSING_SECRET_KEY_MESSAGE = (
    "SECRET_KEY não definida. Gere uma com "
    '`python -c "import secrets; print(secrets.token_hex(32))"` '
    "e coloque no arquivo .env (veja .env.example)."
)


def create_app(config: Config | None = None) -> Flask:
    config = config or Config()
    if not config.secret_key:
        raise RuntimeError(MISSING_SECRET_KEY_MESSAGE)

    app = Flask(__name__, static_folder=None)
    app.config.update(
        APP_CONFIG=config,
        SECRET_KEY=config.secret_key,
        ALLOW_REGISTRATION=config.allow_registration,
        IS_DEMO=config.is_demo,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    engine = create_engine_with_pragmas(config.database_url)
    app.extensions["db_engine"] = engine
    app.extensions["db_session_factory"] = make_session_factory(engine)

    init_auth(app)
    app.register_blueprint(health_bp)
    for blueprint in (auth_bp, demo_bp, properties_bp, records_bp, payments_bp, views_bp):
        app.register_blueprint(blueprint)
    _register_error_handlers(app)
    _register_frontend_routes(app, config.frontend_dist_dir)

    @app.teardown_appcontext
    def _close_db_session(exception: BaseException | None) -> None:
        session = g.pop("db_session", None)
        if session is not None:
            session.close()

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(RequestValidationError)
    def _handle_validation_error(error: RequestValidationError):
        return jsonify(error="validation_error", details=error.details), 400


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
        if is_api_path(request.path):
            return jsonify(error="not_found"), 404
        return _index_response()

    @app.get("/")
    @app.get("/<path:path>")
    def _serve_frontend(path: str = ""):
        if is_api_path(f"/{path}"):
            abort(404)
        target = dist_dir / path
        if path and target.is_file():
            return send_from_directory(dist_dir, path)
        return _index_response()
