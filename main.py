import sqlite3
import datetime
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
    if res:
        return res.fetchone()[0]


def get_person_data(email: str) -> dict[str, int | str]:
    users_attrs = ("id", "name", "surename", "email", "pwdhash", "user_type")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM users WHERE users.email = ?", (email,))
    if res:
        res = res.fetchone()
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


@app.route("/", methods=["GET"])
def home():
    if is_loggedin():
        return render_template(
            "home.html", status=f"YOU ARE LOGGED IN WITH THE EMAIL {session['email']}"
        )
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", action="login")

    try:
        email = request.form["email"]
        password = request.form["password"]
    except KeyError:
        return render_template("login.html", error="invalid form data")

    pwdhash = get_person_data(email).get("pwdhash")

    if not pwdhash:
        return render_template("login.html", error="email not found")

    if pwdhash != md5(password.encode()).hexdigest():
        return render_template("login.html", error="wrong password")

    session["email"] = email
    session["pwdhash"] = pwdhash
    return redirect(url_for("home"))


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")

    try:
        email = request.form["email"]
        name = request.form["name"]
        surename = request.form["surename"]
        birthday = request.form["birthday"]
        password = request.form["password"]
    except:
        return render_template("signin.html", error="invalid form data")

    try:
        datetime.strptime(birthday, "%Y-%m-%d")
    except ValueError:
        return render_template("signin.html", error="invalid birthday")

    if not re.fullmatch(EMAIL_REGEX, email):
        return render_template("signin.html", error="invalid email")

    if get_person_data(email):
        return render_template("signin.html", error="this email exsits already")

    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO users VALUES(?, ?, ?, ?)
    """
    )  # INSERT INTO users (email, name, surename, birthday, pwdhash) VALUES()


@app.route("/images/<image>", methods=["GET"])
def send_image(image):
    return send_file(f"images/{image}")


@app.route("/css/<css>", methods=["GET"])
def send_css(css):
    return send_file(f"css/{css}")


if __name__ == "__main__":
    app.run(debug=True)
