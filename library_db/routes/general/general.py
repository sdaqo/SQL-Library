from flask import Blueprint, render_template, session, current_app
from library_db.utils.utils import get_template_vars

general_bluep = Blueprint("genneral_bluep", __name__, template_folder="templates")

visit_counter = 0


@general_bluep.route("/", methods=["GET"])
def home():
    global visit_counter

    visit_counter += 1
    current_app.logger.info(f"Home Page visited {visit_counter} times.")
    template_vars = get_template_vars(session)
    return render_template("general/index.html", **template_vars)
