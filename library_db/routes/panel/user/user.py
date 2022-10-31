from hashlib import md5
from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    render_template,
    request,
    abort,
    Response,
)


from library_db.utils.utils import (
    is_loggedin,
    get_template_vars,
)
from library_db.utils.db_utils import (
    get_user_data,
    get_user_borrowings,
    get_media,
    estimate_return_date,
)


user_bluep = Blueprint("user_bluep", __name__, template_folder="templates")


@user_bluep.route("/", methods=["GET"])
def redirect_profile():
    return redirect(url_for("panel_bluep.user_bluep.user_profile"))


@user_bluep.route("/profile", methods=["GET"])
def user_profile():
    if not is_loggedin(session):
        return redirect(url_for("auth_bluep.login", next="/me/profile"))

    user_data = get_user_data(session["email"])
    template_vars = get_template_vars(session)

    template_vars["surename"] = user_data.get("surename")
    template_vars["email"] = user_data.get("email")
    template_vars["user_type"] = user_data.get("user_type")
    template_vars["birthday"] = user_data.get("birthday")

    return render_template("user/profile.html", **template_vars)


@user_bluep.route("/borrowings", methods=["GET"])
def user_borrowings():
    if not is_loggedin(session):
        return redirect(url_for("auth_bluep.login", next="/me/borrowings"))

    borrowings = get_user_borrowings(get_user_data(session.get("email")).get("id"))
    table_data = [
        (i, get_media(i.media_id), estimate_return_date(i.media_id).__str__())
        for i in borrowings
    ]

    template_vars = get_template_vars(session)
    template_vars["table_data"] = table_data

    return render_template("user/borrowings.html", **template_vars)


@user_bluep.route("/delete", methods=["POST"])
def delete_user():
    if not is_loggedin(session):
        return redirect(url_for("auth_bluep.login", next="/me/profile"))

    if not request.form.get("password"):
        return abort(Response("Bad Form Data", 400))

    password = request.form["password"]
    pwdhash = get_user_data(session["email"]).get("pwdhash")

    if pwdhash != md5(password.encode()).hexdigest():
        return abort(Response("Wrong Password", 401))

    return redirect(url_for("auth_bluep.login", next="/me/profile"))
