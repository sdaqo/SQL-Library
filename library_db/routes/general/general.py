from flask import Blueprint, render_template, session
from library_db.utils import get_template_vars, get_person_data, is_loggedin

general_bluep = Blueprint("genneral_bluep", __name__, template_folder="templates")


@general_bluep.route("/", methods=["GET"])
def home():
    template_vars = get_template_vars(session)

    if is_loggedin(session):
        template_vars["name"] = get_person_data(session.get("email")).get("name")

    return render_template("general/index.html", **template_vars)
