from flask import Blueprint, session

from library_db.utils.db_utils import (
    get_media,
    is_media_borrowed,
    estimate_return_date,
    get_user_data,
    borrow_book,
    get_borrowing,
    return_book,
)
from library_db.utils.utils import is_loggedin

api_bluep = Blueprint("api_bluep", __name__, template_folder="templates")


@api_bluep.route("/media/<int:media_id>", methods=["GET"])
def media(media_id):
    media_info = get_media(media_id).__dict__
    media_info.update({"is_borrowed": is_media_borrowed(media_id)})
    media_info.update({"estimated_return": estimate_return_date(media_id).__str__()})
    return media_info


@api_bluep.route("/user/borrow/<int:media_id>", methods=["POST"])
def borrow(media_id):
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 403

    user_id = get_user_data(session.get("email")).get("id")

    if not get_media(media_id):
        return {"error": "Media not Found"}, 400

    if is_media_borrowed(media_id):
        return {"error": "Media is already Borrowed"}, 400

    borrow_book(media_id, user_id)

    return {"status": "success"}


@api_bluep.route("/user/return/<int:media_id>", methods=["POST"])
def return_book(media_id):
    if not is_loggedin(session):
        return {"error": "Not Logged in"}, 403

    user_id = get_user_data(session.get("email")).get("id")

    borrowing = get_borrowing(media_id, user_id)

    if borrowing:
        return_book(borrowing.id)
        return {"status": "success"}
    else:
        return {"error": "Borrowing Not Found"}, 400
 	1984 	George Orwell 	15 	Borrowed
Book 	Harry Potter and the Chamber of Secrets 	J. K Rowling 	12 	Borrowed
Book 	Harry Potter and the Sorcerer's Stone 	J. K Rowling 	12 	Borrowed
Book 	The Power of Habit: Why We Do What We Do in Life and Business 	Charles Duhigg 	0 	Avalible 