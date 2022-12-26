from pathlib import Path
from file_read_backwards import FileReadBackwards
from flask import Blueprint, session, request, current_app, send_file

from library_db.utils.db_utils import (
    get_media,
    is_media_borrowed,
    estimate_return_date,
    author_query_mini,
    media_query_mini,
    user_query_mini,
    get_borrower,
)
from library_db.utils.utils import (
    is_admin,
    goodreads_search,
    scrape_goodreads_cover,
    imdb_search,
    musicbrainz_search,
)
from library_db.logger import (
    get_info_logfile,
    get_error_logfile,
)

other_bluep = Blueprint("other_bluep", __name__)


@other_bluep.route("/media/<int:media_id>", methods=["GET"])
def media(media_id):
    media_info = get_media(media_id)
    if not media_info:
        return {"error": "No media with this ID found"}

    media_info = media_info.__dict__
    if is_media_borrowed(media_id):
        media_info.update({"is_borrowed": True})
        media_info.update(
            {"estimated_return": estimate_return_date(media_id).__str__()}
        )
        media_info.update({"borrower": " ".join(get_borrower(media_id))})
    else:
        media_info.update({"is_borrowed": False})

    return media_info


@other_bluep.route("/media/image/<int:media_id>", methods=["GET"])
def media_image(media_id):
    media_info = get_media(media_id)
    if not media_info:
        return {"error": "No media with this ID found"}

    if media_info.image:
        path = Path(current_app.config["UPLOAD_FOLDER"]).joinpath(media_info.image)
        if path.exists():
            return send_file(path, mimetype="image/jpeg")

    return {"error": "Image does not exsist for this media."}


@other_bluep.route("/mini_search/author", methods=["POST"])
def query_authors():
    if not (request.is_json and "query" in request.get_json()):
        return {"error": "Unprocessable data"}, 400

    query = request.get_json()["query"]
    query_res = author_query_mini(query)

    return {"results": query_res}


@other_bluep.route("/mini_search/media", methods=["POST"])
def query_media():
    if not (request.is_json and "query" in request.get_json()):
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


@other_bluep.route("/admin/log", methods=["POST"])
def get_log():
    if not is_admin(session):
        return {"error": "Insufficent Permissions"}, 403

    level = request.get_json().get("level", "info")
    offset = request.get_json().get("offset", None)

    if level == "info":
        log_file = get_info_logfile()
    else:
        log_file = get_error_logfile()

    with open(log_file, "r") as f:
        line_count = sum(1 for _ in f)

    response = {"line_count": line_count, "level": level}

    if offset and offset < line_count:
        backwards_lines = line_count - offset
        lines = []
        with FileReadBackwards(log_file, encoding="utf-8") as frb:
            for _ in range(backwards_lines):
                lines.append(frb.readline())

        lines.reverse()
        response.update({"log_lines": lines})

    return response


@other_bluep.route("/scraper/search_covers", methods=["POST"])
def search_covers():
    if not (
        request.is_json
        and "query" in request.get_json()
        and "media_type" in request.get_json()
    ):
        return {"error": "Unprocessable data"}, 400

    json_data = request.get_json()

    if json_data.get("media_type") == "Book":
        try:
            urls = goodreads_search(json_data.get("query"))
        except:
            return {"error": "Search failed"}

        with_images = False
    elif (
        json_data.get("media_type") == "Blu-Ray"
        or json_data.get("media_type") == "DVD"
    ):
        urls = imdb_search(json_data.get("query"))
        with_images = True
    elif json_data.get("media_type") == "CD":
        urls = musicbrainz_search(json_data.get("query"), json_data.get("artist"))
        with_images = True
    else:
        return {"error": "Invalid media type"}

    return {"with_images": with_images, "urls": urls}


@other_bluep.route("/scraper/book/scrape_cover", methods=["POST"])
def scrape_coverurl():
    if not (request.is_json and "url" in request.get_json()):
        return {"error": "Unprocessable data"}, 400

    url = scrape_goodreads_cover(request.get_json().get("url"))
    if not url:
        return {"error": "Could not scrape image url"}

    return {"image_url": url}
