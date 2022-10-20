from flask import Blueprint, session, redirect
from library_db.utils import get_template_vars

media_bluep = Blueprint("media_bluep", __name__, template_folder="templates")

@media_bluep.route("/medialist", methods=["GET"])
def show_medialist():
    template_vars = get_template_vars(session)
    return render_template("media/medialist.html", **template_vars)