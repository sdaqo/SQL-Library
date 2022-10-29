from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    render_template,
    request,
    abort,
)


from library_db.utils.utils import (
    is_loggedin,
    get_template_vars,
    is_admin,
    is_staff,
)
from library_db.utils.db_utils import (
    get_media,
    author_exsists,
    get_media_types,
    get_media_type_id,
    add_media_item,
    get_author_id,
    add_author_to_db,
    delete_media,
    get_media_id,
    update_media,
    update_author,
    get_author_by_id,
)

staff_bluep = Blueprint("staff_bluep", __name__, template_folder="templates")


@staff_bluep.route("/", methods=["GET"])
def redirect_staff():
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))


@staff_bluep.route("/addremove", methods=["GET"])
def staff_panel_addremove():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    template_vars = get_template_vars(session)
    template_vars["media_error"] = request.args.get("media_error")
    template_vars["author_error"] = request.args.get("author_error")
    template_vars["remove_media_error"] = request.args.get("remove_media_error")
    return render_template("staff/add_remove.html", **template_vars)


@staff_bluep.route("/alter", methods=["GET"])
def staff_panel_alter():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    template_vars = get_template_vars(session)

    if request.args.get("media", None):
        media_id = get_media_id(request.args["media"])
        if media_id:
            template_vars["media_item"] = get_media(media_id)
        else:
            template_vars["media_not_found"] = True
    elif request.args.get("author", None):
        author_id = get_author_id(request.args["author"])
        if author_id:
            template_vars["author"] = (
                request.args["author"],
                get_author_id(request.args["author"]),
            )
        else:
            template_vars["author_not_found"] = True

    template_vars["media_error"] = request.args.get("media_error")
    template_vars["author_error"] = request.args.get("author_error")
    return render_template("staff/alter.html", **template_vars)


@staff_bluep.route("/alter/media", methods=["POST"])
def alter_media():
    def ret_error(error: str):
        return redirect(
            url_for("panel_bluep.staff_bluep.staff_panel_alter", media_error=error)
        )

    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    try:
        id = request.form["id"]
        title = request.form["title"]
        author = request.form["author"]
        media_type = request.form["media_type"]
        isbn = request.form.get("isbn", None)
        age_limit = request.form.get("age_limit", None, int)
    except KeyError:
        return ret_error("Bad Form Data")

    try:
        id = int(id)
        if isbn:
            isbn = int(isbn)
    except ValueError:
        return ret_error("Bad Form Data")

    media = get_media(id)

    if not media:
        return ret_error("Bad Form Data")

    if not media.title == title:
        media_title_id = get_media_id(title)
        if media_title_id:
            return ret_error("Media With this Title already exsists")

    if not age_limit:
        return ret_error("Bad Form Data")

    if not media_type in get_media_types():
        return ret_error("Media Type doesnt exsist")

    media_type = get_media_type_id(media_type)

    if not author_exsists(author):
        return ret_error("Author does not exsist")

    author = get_author_id(author)

    update_media(
        id=id,
        title=title,
        author_id=author,
        age_limit=age_limit,
        media_type_id=media_type,
        isbn=isbn,
    )

    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_alter"))


@staff_bluep.route("/alter/author", methods=["POST"])
def alter_author():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    author_name = request.form.get("name", None)
    id = request.form.get("id", None, int)

    if not author_name or not id:
        return redirect(
            url_for(
                "panel_bluep.staff_bluep.staff_panel_alter",
                author_error="Bad Form Data",
            )
        )

    author = get_author_by_id(id)

    if not author:
        return redirect(
            url_for(
                "panel_bluep.staff_bluep.staff_panel_alter",
                author_error="Bad Form Data",
            )
        )

    if not author == author_name:
        author_id = get_author_id(author_name)
        if author_id:
            return redirect(
                url_for(
                    "staff_bluep.staff_panel_alter",
                    author_error="Author with this Name already exsists",
                )
            )

    update_author(id, author_name)

    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_alter"))


@staff_bluep.route("/addremove/add/media", methods=["POST"])
def add_media():
    def ret_error(error: str):
        return redirect(
            url_for("panel_bluep.staff_bluep.staff_panel_addremove", media_error=error)
        )

    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    try:
        title = request.form["title"]
        author = request.form["author"]
        media_type = request.form["media_type"]
        isbn = request.form.get("isbn", None)
        age_limit = request.form.get("age_limit", None, int)
    except KeyError:
        return ret_error("Bad Form Data")

    if isbn:
        try:
            isbn = int(isbn)
        except ValueError:
            return ret_error("ISBN has to be Number")

    if get_media_id(title):
        return ret_error("Media with this Title already exsists")

    if not age_limit:
        return ret_error("Bad Form Data")

    if not media_type in get_media_types():
        return ret_error("Media Type doesnt exsist")

    media_type = get_media_type_id(media_type)

    if not author_exsists(author):
        return ret_error("Author does not exsist")

    author = get_author_id(author)

    add_media_item(
        title=title,
        author_id=author,
        age_limit=age_limit,
        media_type_id=media_type,
        isbn=isbn,
    )

    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))


@staff_bluep.route("/addremove/add/author", methods=["POST"])
def add_author():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    author = request.form.get("author", None)

    if not author:
        return redirect(
            url_for(
                "panel_bluep.staff_bluep.staff_panel_addremove",
                author_error="Bad Form Data",
            )
        )

    if author_exsists(author):
        return redirect(
            url_for(
                "staff_bluep.staff_panel_addremove",
                author_error="Author Already exsists",
            )
        )

    add_author_to_db(author)

    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))


@staff_bluep.route("/addremove/remove/media", methods=["POST"])
def remove_media():
    if not is_loggedin(session):
        return abort(403)

    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    media = request.form.get("media", None)

    if not media:
        return redirect(
            url_for(
                "staff_bluep.staff_panel_addremove", remove_media_error="Bad Form Data"
            )
        )

    media_id = get_media_id(media)
    if not media_id:
        return redirect(
            url_for(
                "staff_bluep.staff_panel_addremove",
                remove_media_error="Media Not Found",
            )
        )

    delete_media(media_id)
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))
