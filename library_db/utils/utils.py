from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
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
    if not is_loggedin(session):
        return False

    if not get_user_type(session["email"]) == "Staff":
        return False

    return True


def is_admin(session):
    if not is_loggedin(session):
        return False

    if not get_user_type(session["email"]) == "Admin":
        return False

    return True


def get_template_vars(session) -> dict:
    template_vars = {}
    template_vars["logged_in"] = is_loggedin(session)
    template_vars["is_admin"] = is_admin(session)
    template_vars["is_staff"] = is_staff(session)
    template_vars["darkmode"] = session.get("darkmode")
    template_vars["name"] = get_user_data(session.get("email")).get("name")
    template_vars["media_types"] = get_media_types()
    return template_vars


def update_query_params(url: str, **params):
    parsed_url = urlparse(url)
    parsed_query = dict(parse_qs(parsed_url.query), **params)
    return urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            urlencode(parsed_query, doseq=True),
            parsed_url.fragment,
        )
    )
