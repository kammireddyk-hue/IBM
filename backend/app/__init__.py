from pathlib import Path

from flask import Flask

from .routes import api


def create_app(test_config=None):
    frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path="/assets",
    )
    app.config.from_mapping(
        DATASET_DIR=Path(__file__).resolve().parents[2],
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    app.register_blueprint(api, url_prefix="/api/v1")

    @app.get("/")
    def frontend():
        return app.send_static_file("index.html")

    return app
