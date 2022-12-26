import uuid
from pathlib import Path
from werkzeug.datastructures import FileStorage
from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    render_template,
    request,
    abort,
    current_app,
)

from library_db.utils.utils import (
    get_template_vars,
    is_admin,
    is_staff,
    process_cover_image,
    process_cd_cover,
    download_image
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



ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}

def allowed_file(filename):
    return Path(filename).suffix in ALLOWED_EXTENSIONS

@staff_bluep.route("/", methods=["GET"])
def redirect_staff():
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))


@staff_bluep.route("/addremove", methods=["GET"])
def staff_panel_addremove():
    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    template_vars = get_template_vars(session)
    template_vars["media_error"] = request.args.get("media_error")
    template_vars["author_error"] = request.args.get("author_error")
    template_vars["remove_media_error"] = request.args.get("remove_media_error")
    return render_template("staff/add_remove.html", **template_vars)


@staff_bluep.route("/alter", methods=["GET"])
def staff_panel_alter():
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
    
    if age_limit is None:
        age_limit = 0

    if not media_type in get_media_types():
        return ret_error("Media Type doesnt exsist")

    media_type = get_media_type_id(media_type)

    if not author_exsists(author):
        return ret_error("Author does not exsist")

    author = get_author_id(author)


    filename = media.image
    if "image" in request.files:
        file = request.files["image"]
        if not file.filename == '' and allowed_file(file.filename):
            if not filename:
                filename = uuid.uuid1().hex + ".jpg"
            
            save_path = Path(current_app.config['UPLOAD_FOLDER']).joinpath(filename).__str__()
            file.save(save_path)
            process_cover_image(save_path)

    update_media(
        id=id,
        title=title,
        author_id=author,
        age_limit=age_limit,
        media_type_id=media_type,
        image=filename,
        isbn=isbn
    )

    current_app.logger.info(
        f"{session['email']} Updated media {media.title} with id {id}"
    )
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_alter"))


@staff_bluep.route("/alter/author", methods=["POST"])
def alter_author():
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
                    "panel_bluep.staff_bluep.staff_panel_alter",
                    author_error="Author with this Name already exsists",
                )
            )

    update_author(id, author_name)

    current_app.logger.info(f"{session['email']} Updated author {author} with id {id}")
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_alter"))


@staff_bluep.route("/addremove/add/media", methods=["POST"])
def add_media():
    def ret_error(error: str):
        return redirect(
            url_for("panel_bluep.staff_bluep.staff_panel_addremove", media_error=error)
        )

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
            return ret_error("ISBN has to be a Number")

    if get_media_id(title):
        return ret_error("Media with this Title already exsists")

    if age_limit is None:
        return ret_error("Bad Form Data")

    if not media_type in get_media_types():
        return ret_error("Media Type doesnt exsist")

    media_type_id = get_media_type_id(media_type)

    if not author_exsists(author):
        return ret_error("Author does not exsist")

    author_id = get_author_id(author)

    filename = None
    if "image" in request.files or "url" in request.form:
        file = request.files.get("image", FileStorage(filename=""))
        url = request.form.get("url", "")
        filename = uuid.uuid1().hex + ".jpg"
        save_path = Path(current_app.config['UPLOAD_FOLDER']).joinpath(filename).__str__()

        if file.filename != '' and url != '':
            return ret_error("Can't upload Image and use Scraper Image")
        elif not file.filename == '' and allowed_file(file.filename):
            file.save(save_path)
            if media_type == "CD":
                process_cd_cover(save_path)
            else:
                process_cover_image(save_path)
        elif not url == '':
            if download_image(url, save_path) != 1:
                filename = None
            else:
                if media_type == "CD":
                    process_cd_cover(save_path)
                else:
                    process_cover_image(save_path)
        else:
            filename = None

    new_id = add_media_item(
        title=title,
        author_id=author_id,
        age_limit=age_limit,
        media_type_id=media_type_id,
        isbn=isbn,
        image=filename
    )

    current_app.logger.info(f"{session['email']} Added media {title} with id {new_id}")
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))


@staff_bluep.route("/addremove/add/author", methods=["POST"])
def add_author():
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
                "panel_bluep.staff_bluep.staff_panel_addremove",
                author_error="Author Already exsists",
            )
        )

    new_id = add_author_to_db(author)

    current_app.logger.info(f"{session['email']} Added author with id {new_id}")
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))


@staff_bluep.route("/addremove/remove/media", methods=["POST"])
def remove_media():
    if not (is_staff(session) or is_admin(session)):
        return abort(403)

    media = request.form.get("media", None)

    if not media:
        return redirect(
            url_for(
                "panel_bluep.staff_bluep.staff_panel_addremove",
                remove_media_error="Bad Form Data",
            )
        )

    media_id = get_media_id(media)
    if not media_id:
        return redirect(
            url_for(
                "panel_bluep.staff_bluep.staff_panel_addremove",
                remove_media_error="Media Not Found",
            )
        )

    delete_media(media_id, current_app.config['UPLOAD_FOLDER'])
    current_app.logger.info(
        f"{session['email']} Removed media {media} with id {media_id}"
    )
    return redirect(url_for("panel_bluep.staff_bluep.staff_panel_addremove"))
