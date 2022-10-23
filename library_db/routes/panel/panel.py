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


from library_db.database import get_db_connection
from library_db.utils.utils import (
    is_loggedin,
    get_template_vars,
    is_admin,
    is_staff,
)
from library_db.utils.db_utils import (
    get_user_data,
    get_user_borrowings,
    get_media,
    estimate_return_date,
    author_exsists,
    get_media_types,
    get_media_type_id,
    add_media_item,
    get_author_id,
    add_author_to_db,
    delete_media,
    get_media_id,
)

panel_bluep = Blueprint("panel_bluep", __name__, template_folder="templates")
con = get_db_connection()


@panel_bluep.route("/me", methods=["GET"])
def redirect_profile():
    return redirect(url_for("panel_bluep.user_profile"))


@panel_bluep.route("/me/profile", methods=["GET"])
def user_profile():
    if not is_loggedin(session):
        return redirect(url_for("auth_bluep.login", next="/me/profile"))

    user_data = get_user_data(session["email"])
    template_vars = get_template_vars(session)

    template_vars["surename"] = user_data.get("surename")
    template_vars["email"] = user_data.get("email")
    template_vars["user_type"] = user_data.get("user_type")
    template_vars["birthday"] = user_data.get("birthday")

    return render_template("panel/user/profile.html", **template_vars)


@panel_bluep.route("/me/borrowings", methods=["GET"])
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

    return render_template("panel/user/borrowings.html", **template_vars)


@panel_bluep.route("/me/delete", methods=["POST"])
def delete_user():
    if not is_loggedin(session):
        return redirect(url_for("auth_bluep.login", next="/me/profile"))

    if not request.form.get("password"):
        return abort(Response("Bad Form Data", 400))

    password = request.form["password"]
    pwdhash = get_user_data(session["email"]).get("pwdhash")

    if pwdhash != md5(password.encode()).hexdigest():
        return abort(Response("Wrong Password", 401))


@panel_bluep.route("/staff", methods=["GET"])
def redirect_staff():
    return redirect(url_for("panel_bluep.staff_panel_addremove"))


@panel_bluep.route("/staff/addremove", methods=["GET"])
def staff_panel_addremove():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    template_vars = get_template_vars(session)
    template_vars["media_error"] = request.args.get("media_error")
    template_vars["author_error"] = request.args.get("author_error")
    template_vars["remove_media_error"] = request.args.get("remove_media_error")
    return render_template("panel/staff/add_remove.html", **template_vars)


@panel_bluep.route("/staff/alter", methods=["GET"])
def staff_panel_alter():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    template_vars = get_template_vars(session)
    return render_template("panel/staff/alter.html", **template_vars)


@panel_bluep.route("/staff/addremove/add/media", methods=["POST"])
def add_media():
    def ret_error(error: str):
        return redirect(url_for("panel_bluep.staff_panel_addremove", media_error=error))

    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    try:
        title = request.form["title"]
        author = request.form["author"]
        media_type = request.form["media_type"]
        isbn = request.form.get("isbn", "NULL")
        age_limit = request.form.get("age_limit", None, int)
    except KeyError:
        return ret_error("Bad Form Data")

    if not age_limit:
        return ret_error("Bad Form Data")

    if not media_type in get_media_types():
        return ret_error("Media Type doesnt Exsist")

    media_type = get_media_type_id(media_type)

    if not author_exsists(author):
        return ret_error("Author does not exsist")

    author = get_author_id(author)

    add_media_item(
        title=title,
        author=author,
        age_limit=age_limit,
        media_type=media_type,
        isbn=isbn,
    )

    return redirect(url_for("panel_bluep.staff_panel_addremove"))


@panel_bluep.route("/staff/addremove/add/author", methods=["POST"])
def add_author():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    author = request.form.get("author", None)

    if not author:
        return redirect(
            url_for("panel_bluep.staff_panel_addremove", author_error="Bad Form Data")
        )

    if author_exsists(author):
        return redirect(
            url_for(
                "panel_bluep.staff_panel_addremove",
                author_error="Author Already exsists",
            )
        )

    add_author_to_db(author)

    return redirect(url_for("panel_bluep.staff_panel_addremove"))


@panel_bluep.route("/staff/addremove/remove/media", methods=["POST"])
def remove_media():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    media = request.form.get("media", None)

    if not media:
        return redirect(
            url_for(
                "panel_bluep.staff_panel_addremove", remove_media_error="Bad Form Data"
            )
        )

    media_id = get_media_id(media)
    if not media_id:
        return redirect(
            url_for(
                "panel_bluep.staff_panel_addremove",
                remove_media_error="Media Not Found",
            )
        )

    delete_media(media_id)
    return redirect(url_for("panel_bluep.staff_panel_addremove"))
