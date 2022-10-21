from flask import Flask
from flask_cors import CORS
from library_db.routes import (
    auth_bluep,
    general_bluep,
    misc_bluep,
    media_bluep,
    api_bluep,
)

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADER"] = "Content-Type"

app.secret_key = "c4c4f1e8c78c2a52ee46"
app.register_blueprint(auth_bluep)
app.register_blueprint(general_bluep)
app.register_blueprint(misc_bluep)
app.register_blueprint(media_bluep)
app.register_blueprint(api_bluep, url_prefix="/api")


if __name__ == "__main__":
    app.run(debug=True)
