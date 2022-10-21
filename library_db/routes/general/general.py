from flask import Blueprint, render_template, session
from library_db.utils.utils import get_template_vars, is_loggedin

general_bluep = Blueprint("genneral_bluep", __name__, template_folder="templates")


@general_bluep.route("/", methods=["GET"])
def home():
    template_vars = get_template_vars(session)

    return render_template("general/index.html", **template_vars)
