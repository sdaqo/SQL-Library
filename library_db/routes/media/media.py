from flask import Blueprint, session, redirect, render_template, request
from library_db.utils import get_template_vars
from library_db.database import get_db_connection
from dataclasses import dataclass

media_bluep = Blueprint("media_bluep", __name__, template_folder="templates")
con = get_db_connection()

PAGE_SIZE = 30


@dataclass
class MediaItem:
    id: int
    title: str | None
    age_limit: int | None
    media_type: str | None
    author: str | None
    is_borrowed: bool | None


def is_media_borrowed(media_id: int) -> bool:
    statement = """
        SELECT borrow_date
        FROM borrowings
        WHERE media_id = ? AND return_date IS NULL
        """
    cur = con.cursor()
    res = cur.execute(statement, (media_id,))
    res = res.fetchone()
    if res:
        return True

    return False


def get_media_list(
    limit: int,
    offset: int,
    media_type: str = None,
    query: str = "",
    sort: str = "title",
    sort_type: int = 0,
) -> [MediaItem]:

    media_types = ["Book", "DVD", "CD", "Blu-Ray"]
    sorts = {
        "id": "media.id",
        "title": "media.title",
        "age_limit": "age_limit",
        "author": "authors.name",
    }

    if sort_type == 1:
        sort_type = "DESC"
    else:
        sort_type = "ASC"

    statement = f"""
        SELECT media.id, media.title, media.age_limit, media_types.title, authors.name
        FROM media
        JOIN media_types ON media.media_type_id  = media_types.id
        JOIN authors ON media.author_id = authors.id
        WHERE media.title LIKE ? {"AND media_types.title = '%s'" % media_type if media_type in media_types else ""}
        ORDER BY {"%s %s" % (sorts[sort], sort_type) if sort in sorts.keys() else "%s %s" % (sorts["title"], sort_type)}
        LIMIT ?
        OFFSET ?
        """
    print(statement)

    cur = con.cursor()
    res = cur.execute(statement, ("%" + query + "%", limit, offset))
    res = res.fetchall()

    if res:
        return [
            MediaItem(*item, is_borrowed=is_media_borrowed(item[0])) for item in res
        ]

    return []


@media_bluep.route("/medialist", methods=["GET"])
def show_medialist():
    allowed_query_params = ["sort", "query", "media_type", "sort_type"]
    query_params = {}
    for name, value in request.args.items():
        if name in allowed_query_params:
            query_params.update({name: value})
    #TODO author querying
    template_vars = get_template_vars(session)
    template_vars["table_data"] = get_media_list(10, 0, **query_params)
    return render_template("media/medialist.html", **template_vars)
