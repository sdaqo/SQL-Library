import re
from hashlib import md5
from datetime import datetime
from flask import Blueprint, render_template, session, request, redirect, current_app

from library_db.database import get_db_connection
from library_db.utils.utils import get_template_vars, is_admin
from library_db.utils.db_utils import get_user_data

auth_bluep = Blueprint("auth_bluep", __name__, template_folder="templates")
con = get_db_connection()
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


@auth_bluep.route("/logout", methods=["GET"])
def logout():
    session.pop("email", None)
    session.pop("pwdhash", None)

    return redirect("/")


@auth_bluep.route("/login", methods=["GET", "POST"])
def login():
    template_vars = get_template_vars(session)
    template_vars["next"] = request.args.get("next", "/")

    def ret_error(error: str):
        return render_template("auth/login.html", error=error, **template_vars)

    if request.method == "GET":
        return render_template("auth/login.html", **template_vars)

    try:
        email = request.form["email"]
        password = request.form["password"]
    except KeyError:
        return ret_error("invalid form data")

    pwdhash = get_user_data(email).get("pwdhash")

    if not pwdhash:
        return ret_error("email not found")

    if pwdhash != md5(password.encode()).hexdigest():
        current_app.logger.info(f'User with email "{email}" failed to login')
        return ret_error("wrong password")

    session["email"] = email
    session["pwdhash"] = pwdhash
    current_app.logger.info(f'User with email "{email}" logged in')

    return redirect(request.args.get("next", "/"))


@auth_bluep.route("/signin", methods=["GET", "POST"])
def signin():
    template_vars = get_template_vars(session)
    if request.method == "GET":
        return render_template("auth/signin.html", **template_vars)

    def ret_error(error: str):
        return render_template("auth/signin.html", error=error, **template_vars)

    try:
        email = request.form["email"]
        name = request.form["name"]
        surename = request.form["surename"]
        birthday = request.form["birthday"]
        password = request.form["password"]
        usertype = request.form["usertype"]
    except KeyError:
        return ret_error("invalid form data")

    try:
        datetime.strptime(birthday, "%Y-%m-%d")
    except ValueError:
        return ret_error("invalid birthday")

    if not re.fullmatch(EMAIL_REGEX, email):
        return ret_error("invalid email")

    if get_user_data(email):
        return ret_error("this email exsits already")

    if not usertype in ["2", "1", "5"]:
        if not (is_admin(session) and usertype in ["3", "4"]):
            return ret_error("invalid usertype")

    pwdhash = md5(password.encode()).hexdigest()
    cur = con.cursor()
    cur.execute(
        """INSERT INTO users (email, name, surename, birthday, pwdhash, user_type)
           VALUES(?, ?, ?, ?, ?, ?)""",
        (
            email,
            name,
            surename,
            birthday,
            pwdhash,
            int(usertype),
        ),
    )

    con.commit()

    current_app.logger.info(
        f'New user "{name} {surename}" with email "{email}" created'
    )

    return redirect("/")
