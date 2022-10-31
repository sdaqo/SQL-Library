from flask import Blueprint, session, request


from library_db.utils.db_utils import (
    get_media,
    is_media_borrowed,
    estimate_return_date,
    author_query_mini,
    media_query_mini,
    user_query_mini,
    get_borrower,
)
from library_db.utils.utils import is_admin

other_bluep = Blueprint("other_bluep", __name__)


@other_bluep.route("/media/<int:media_id>", methods=["GET"])
def media(media_id):
    media_info = get_media(media_id).__dict__
    if is_media_borrowed(media_id):
        media_info.update({"is_borrowed": True})
        media_info.update(
            {"estimated_return": estimate_return_date(media_id).__str__()}
        )
        media_info.update({"borrower": " ".join(get_borrower(media_id))})
    else:
        media_info.update({"is_borrowed": False})

    return media_info


@other_bluep.route("/mini_search/author", methods=["POST"])
def query_authors():
    if not request.is_json and "query" in request.get_json():
        return {"error": "Unprocessable data"}, 400

    query = request.get_json()["query"]
    query_res = author_query_mini(query)

    return {"results": query_res}


@other_bluep.route("/mini_search/media", methods=["POST"])
def query_media():
    if not request.is_json and "query" in request.get_json():
        return {"error": "Unprocessable data"}, 400

    query = request.get_json()["query"]
    query_res = media_query_mini(query)

    return {"results": query_res}


@other_bluep.route("/admin/mini_search/users", methods=["POST"])
def query_users():
    if not is_admin(session):
        return {"error": "Insufficent Permissions"}, 403

    if not request.is_json and "query" in request.get_json():
        return {"error": "Unprocessable data"}, 400

    query = request.get_json()["query"]
    query_res = user_query_mini(query)

    return {"results": query_res}
