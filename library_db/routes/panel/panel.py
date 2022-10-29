from flask import Blueprint

from library_db.routes.panel.staff import staff_bluep
from library_db.routes.panel.user import user_bluep
from library_db.routes.panel.admin import admin_bluep

panel_bluep = Blueprint("panel_bluep", __name__, template_folder="templates")

panel_bluep.register_blueprint(user_bluep, url_prefix="/me")
panel_bluep.register_blueprint(staff_bluep, url_prefix="/staff")
panel_bluep.register_blueprint(admin_bluep, url_prefix="/admin")
