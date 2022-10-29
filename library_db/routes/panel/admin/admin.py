from flask import Blueprint

admin_bluep = Blueprint("admin_bluep", __name__, template_folder="templates")


@admin_bluep.route("/", methods=["GET"])
def admin_panel():
    return 501
