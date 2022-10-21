from library_db.utils.db_utils import get_user_data, get_user_type, get_media_types


def is_loggedin(session):
    try:
        email = session["email"]
        pwdhash = session["pwdhash"]
    except KeyError:
        return False

    db_pwdhash = get_user_data(email).get("pwdhash")

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

    if not get_user_type(email) == "Staff":
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
    if not get_user_type(email) == "Admin":
        return False

    return True


def get_template_vars(session) -> dict:
    template_vars = {}
    template_vars["logged_in"] = is_loggedin(session)
    template_vars["is_admin"] = is_admin(session)
    template_vars["is_staff"] = is_staff(session)
    template_vars["darkmode"] = session.get("darkmode")
    template_vars["name"] = get_user_data(session.get("email")).get("name")
    template_vars["media_types"] = [i[0] for i in get_media_types()]
    return template_vars
