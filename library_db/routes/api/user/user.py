import re
from hashlib import md5
from datetime import date, datetime
from flask import Blueprint, session, request, current_app


from library_db.utils.db_utils import (
    get_media,
    is_media_borrowed,
    get_user_data,
    borrow_media,
    update_user,
    delete_user,
)
from library_db.utils.utils import is_loggedin

user_bluep = Blueprint("user_bluep", __name__)

EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
validate_json = lambda req: req.is_json and "value" in req.get_json()


@user_bluep.route("/user/borrow/<int:media_id>", methods=["POST"])
def borrow(media_id):
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 401

    user = get_user_data(session.get("email"))

    if not get_media(media_id):
        return {"error": "Media not Found"}, 400

    if is_media_borrowed(media_id):
        return {"error": "Media is already Borrowed"}, 400

    bd = user.get("birthday")
    bd = datetime.strptime(bd, "%Y-%m-%d")
    today = date.today()
    age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    age_limit = get_media(media_id).age_limit

    if age_limit > age:
        return {"error": "User too Young"}

    borrow_media(media_id, user.get("id"))

    current_app.logger.info(f"{session['email']} Borrowed media with id {media_id}")
    return {"status": "success"}


@user_bluep.route("/user/update/name", methods=["POST"])
def update_name():
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 401

    if not validate_json(request):
        return {"error": "Unprocessable data"}, 400

    user_id = get_user_data(session.get("email")).get("id")
    body = request.get_json()

    update_user(user_id, "name", body["value"])

    return {"status": "success"}


@user_bluep.route("/user/update/surename", methods=["POST"])
def update_surename():
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 401

    if not validate_json(request):
        return {"error": "Unprocessable data"}, 400

    user_id = get_user_data(session.get("email")).get("id")
    body = request.get_json()

    update_user(user_id, "surename", body["value"])

    return {"status": "success"}


@user_bluep.route("/user/update/email", methods=["POST"])
def update_email():
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 401

    if not validate_json(request):
        return {"error": "Unprocessable data"}, 400

    user_id = get_user_data(session.get("email")).get("id")
    new_email = request.get_json()["value"]

    if not re.fullmatch(EMAIL_REGEX, new_email):
        return {"error": "Invalid email"}, 400

    if get_user_data(new_email):
        return {"error": "Email Already exsists"}, 400

    update_user(user_id, "email", new_email)

    return {"status": "success"}


@user_bluep.route("/user/update/password", methods=["POST"])
def update_password():
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 401

    if not validate_json(request):
        return {"error": "Unprocessable data"}, 400

    user_id = get_user_data(session.get("email")).get("id")
    new_password = request.get_json()["value"]

    hashed_pw = md5(new_password.encode()).hexdigest()

    update_user(user_id, "pwdhash", hashed_pw)

    return {"status": "success"}


@user_bluep.route("/user/update/birthday", methods=["POST"])
def update_birthday():
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 401

    if not validate_json(request):
        return {"error": "Unprocessable data"}, 400

    user_id = get_user_data(session.get("email")).get("id")
    new_bd = request.get_json()["value"]

    try:
        datetime.strptime(new_bd, "%Y-%m-%d")
    except ValueError:
        return {"error": "invalid birthday"}, 400

    update_user(user_id, "birthday", new_bd)

    return {"status": "success"}


@user_bluep.route("/user/delete", methods=["POST"])
def remove_user():
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 401

    if not request.is_json and "password" in request.get_json():
        return {"error": "Unprocessable data"}, 400

    password = request.get_json().get("password")
    user = get_user_data(session.get("email"))

    if user.get("pwdhash") != md5(password.encode()).hexdigest():
        return {"error": "Wrong Password"}, 401

    delete_user(user.get("id"))

    current_app.logger.info(
        f"{session['email']} Deleted user with email {session['email']}"
    )

    session.pop("email")
    session.pop("pwdhash")

    return {"status": "success"}
