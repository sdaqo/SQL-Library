from flask import Blueprint

from library_db.routes.api.user import user_bluep
from library_db.routes.api.other import other_bluep

api_bluep = Blueprint("api_bluep", __name__)

api_bluep.register_blueprint(user_bluep)
api_bluep.register_blueprint(other_bluep)
