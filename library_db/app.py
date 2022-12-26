import os
import logging
from flask import Flask
from flask_cors import CORS

from library_db.logger import get_handlers, RequestHandler
from library_db.routes import (
    auth_bluep,
    general_bluep,
    misc_bluep,
    media_bluep,
    api_bluep,
    panel_bluep,
)


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config["CORS_HEADER"] = "Content-Type"
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "images/media/")

    app.secret_key = "c4c4f1e8c78c2a52ee46"

    root_logger = logging.getLogger("root")
    for handler in get_handlers():
        root_logger.addHandler(handler)

    app.logger = root_logger
    app.logger.setLevel(logging.DEBUG)

    app.register_blueprint(general_bluep)
    app.register_blueprint(auth_bluep)
    app.register_blueprint(misc_bluep)
    app.register_blueprint(media_bluep)
    app.register_blueprint(panel_bluep)
    app.register_blueprint(api_bluep, url_prefix="/api")

    return app


if __name__ == "__main__":
    new_app = create_app()
    new_app.run(debug=True, request_handler=RequestHandler)
