import sqlite3
from datetime import datetime
import re
from flask import Flask, render_template, session, send_file, request, redirect, url_for
from hashlib import md5
from pathlib import Path

app = Flask(__name__)
con = sqlite3.connect("library.db", check_same_thread=False)

app.secret_key = "c4c4f1e8c78c2a52ee46"

EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


def get_person_type(email: str) -> str:
    statement = """
	  SELECT user_types.title 
	  FROM users 
	  JOIN user_types ON users.user_type = user_types.id 
	  WHERE users.email = ?
	  """

    cur = con.cursor()
    res = cur.execute(statement, (email,))
    res = res.fetchone()
    if res:
        return res[0]


def get_person_data(email: str) -> dict[str, int | str]:
    users_attrs = (
        "id",
        "name",
        "surename",
        "email",
        "pwdhash",
        "user_type",
        "birthday",
    )
    cur = con.cursor()
    res = cur.execute("SELECT * FROM users WHERE users.email = ?", (email,))
    res = res.fetchone()
    if res:
        return {users_attrs[i]: res[i] for i, _ in enumerate(users_attrs)}


def is_loggedin():
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    db_pwdhash = get_person_data(email).get("pwdhash")

    if not db_pwdhash:
        return False

    return db_pwdhash == pwdhash


def is_staff():
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    if not is_loggedin():
        return False

    if not get_person_type(email) == "Staff":
        return False

    return True


def is_admin():
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    if not is_loggedin():
        return False
    if not get_person_type(email) == "Admin":
        return False

    return True


def get_template_vars() -> dict:
    template_vars = {}
    template_vars["logged_in"] = is_loggedin()
    template_vars["is_admin"] = is_admin()
    template_vars["is_staff"] = is_staff()
    template_vars["darkmode"] = session.get("darkmode")
    return template_vars


@app.route("/", methods=["GET"])
def home():
    template_vars = get_template_vars()

    if is_loggedin():
        template_vars["name"] = get_person_data(session.get("email")).get("name")

    return render_template("index.html", **template_vars)


@app.route("/medialist", methods=["GET"])
def show_medialist():
    template_vars = get_template_vars()
    return render_template("medialist.html", **template_vars)


@app.route("/darkmode", methods=["GET"])
def toggle_darkmode():
    darkmode = session.get("darkmode", False)
    session["darkmode"] = not darkmode

    return redirect(request.args.get("ref", "/"))


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("email", None)
    session.pop("pwdhash", None)

    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    template_vars = get_template_vars()

    def ret_error(error: str):
        return render_template("login.html", error=error, **template_vars)

    if request.method == "GET":
        return render_template("login.html", **template_vars)

    try:
        email = request.form["email"]
        password = request.form["password"]
    except KeyError:
        return ret_error("invalid form data")

    pwdhash = get_person_data(email).get("pwdhash")

    if not pwdhash:
        return ret_error("email not found")

    if pwdhash != md5(password.encode()).hexdigest():
        return ret_error("wrong password")

    session["email"] = email
    session["pwdhash"] = pwdhash
    return redirect(url_for("home"))


@app.route("/signin", methods=["GET", "POST"])
def signin():
    template_vars = get_template_vars()
    if request.method == "GET":
        return render_template("signin.html", **template_vars)

    def ret_error(error: str):
        return render_template("login.html", error=error, **template_vars)

    try:
        email = request.form["email"]
        name = request.form["name"]
        surename = request.form["surename"]
        birthday = request.form["birthday"]
        password = request.form["password"]
        usertype = request.form["usertype"]
    except:
        return ret_error("invalid form data")

    try:
        datetime.strptime(birthday, "%Y-%m-%d")
    except ValueError:
        return ret_error("invalid birthday")

    if not re.fullmatch(EMAIL_REGEX, email):
        return ret_error("invalid email")

    if get_person_data(email):
        return ret_error("this email exsits already")

    if not usertype in ["Default", "Teacher", "Student"]:
        return ret_error("invalid usertype")

    pwdhash = md5(password.encode()).hexdigest()
    cur = con.cursor()
    cur.execute(
        """INSERT INTO users (email, name, surename, birthday, pwdhash, user_type) VALUES(?, ?, ?, ?, ?, ?)""",
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

    return redirect(url_for("login"))


@app.route("/images/<image>", methods=["GET"])
def send_image(image):
    return send_file(f"images/{image}")


@app.route("/static/css/<css>", methods=["GET"])
def send_css(css):
    return send_file(f"static/css/{css}")


@app.route("/static/js/<js>", methods=["GET"])
def send_js(js):
    return send_file(f"static/js/{js}")


if __name__ == "__main__":
    app.run(debug=True)
