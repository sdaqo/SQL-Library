import logging
from pathlib import Path
from logging.config import dictConfig
from flask import Flask, request
from flask_cors import CORS
from library_db.routes import (
    auth_bluep,
    general_bluep,
    misc_bluep,
    media_bluep,
    api_bluep,
    panel_bluep,
)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr

        return super().format(record)


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config["CORS_HEADER"] = "Content-Type"

    app.secret_key = "c4c4f1e8c78c2a52ee46"

    log_path = Path(__file__).parent / "logs" / "flask_log"
    log_path.parent.mkdir(exist_ok=True)
    # TODO: Implement this properly
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s]: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                },
                "timed_file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "filename": log_path.__str__(),
                    "when": "D",
                },
            },
            "root": {"level": "DEBUG", "handlers": ["wsgi", "timed_file"]},
        }
    )

    app.register_blueprint(auth_bluep)
    app.register_blueprint(general_bluep)
    app.register_blueprint(misc_bluep)
    app.register_blueprint(media_bluep)
    app.register_blueprint(panel_bluep)
    app.register_blueprint(api_bluep, url_prefix="/api")

    return app


if __name__ == "__main__":
    new_app = create_app()
    new_app.run(debug=True)
