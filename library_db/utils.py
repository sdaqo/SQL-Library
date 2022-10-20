from library_db.database import get_db_connection

con = get_db_connection()


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

    return {}


def is_loggedin(session):
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    db_pwdhash = get_person_data(email).get("pwdhash")

    if not db_pwdhash:
        return False

    return db_pwdhash == pwdhash


def is_staff(session):
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    if not is_loggedin(session):
        return False

    if not get_person_type(email) == "Staff":
        return False

    return True


def is_admin(session):
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    if not is_loggedin(session):
        return False
    if not get_person_type(email) == "Admin":
        return False

    return True


def get_template_vars(session) -> dict:
    template_vars = {}
    template_vars["logged_in"] = is_loggedin(session)
    template_vars["is_admin"] = is_admin(session)
    template_vars["is_staff"] = is_staff(session)
    template_vars["darkmode"] = session.get("darkmode")
    template_vars["name"] = get_person_data(session.get("email")).get("name")
    return template_vars
