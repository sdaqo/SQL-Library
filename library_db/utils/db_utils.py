from datetime import datetime, date, timedelta

from library_db.database import get_db_connection
from library_db.utils.models import MediaItem, User, Borrowing


con = get_db_connection()


def get_user_type(email: str) -> str:
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


def get_user_data(email: str) -> dict[str, str | int]:
    cur = con.cursor()
    res = cur.execute(
        """
        SELECT users.id, users.name, users.surename,
               users.email, users.pwdhash, user_types.title,
               users.birthday
        FROM users 
        JOIN user_types ON users.user_type = user_types.id  
        WHERE users.email = ?""",
        (email,),
    )
    res = res.fetchone()
    if res:
        return User(*res).__dict__

    return {}


def get_media_types():
    cur = con.cursor()
    res = cur.execute("SELECT title FROM media_types")
    res = res.fetchall()
    return res


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


def get_media_query_count(
    query: str = "", author_query: str = "", media_type: str = None
) -> int:
    media_types = ["Book", "DVD", "CD", "Blu-Ray"]

    statement = f"""
        SELECT COUNT(media.title) query_count
        FROM media
        JOIN media_types ON media.media_type_id  = media_types.id
        JOIN authors ON media.author_id = authors.id
        WHERE media.title LIKE ? AND authors.name LIKE ? 
            {"AND media_types.title = '%s'" % media_type if media_type in media_types else ""}
        """

    cur = con.cursor()
    res = cur.execute(statement, ("%" + query + "%", "%" + author_query + "%"))
    res = res.fetchone()

    if res:
        return res[0]

    return 0


def get_media_list(
    limit: int,
    offset: int,
    media_type: str = None,
    author_query: str = "",
    query: str = "",
    sort: str = "title",
    sort_type: str = "ASC",
) -> ([MediaItem], str, str):

    media_types = ["Book", "DVD", "CD", "Blu-Ray"]
    sorts = {
        "id": "media.id",
        "title": "media.title",
        "age_limit": "age_limit",
        "author": "authors.name",
    }

    if sort_type != "DESC":
        sort_type = "ASC"

    if sort not in sorts.keys():
        sort = "title"

    statement = f"""
        SELECT media.id, media.title, media.age_limit, media_types.title, authors.name
        FROM media
        JOIN media_types ON media.media_type_id  = media_types.id
        JOIN authors ON media.author_id = authors.id
        WHERE media.title LIKE ? AND authors.name LIKE ? 
            {"AND media_types.title = '%s'" % media_type if media_type in media_types else ""}
        ORDER BY {sorts[sort]} {sort_type}
        LIMIT ?
        OFFSET ?
        """

    cur = con.cursor()
    res = cur.execute(
        statement, ("%" + query + "%", "%" + author_query + "%", limit, offset)
    )
    res = res.fetchall()

    if res:
        return (
            [MediaItem(*item) for item in res],
            sort,
            sort_type,
        )

    return [], sort, sort_type


def get_media(media_id: int) -> MediaItem | None:
    statement = """
        SELECT media.id, media.title, media.age_limit, media_types.title, authors.name
        FROM media
        JOIN media_types ON media.media_type_id  = media_types.id
        JOIN authors ON media.author_id = authors.id
        WHERE media.id = ?
        """
    cur = con.cursor()
    res = cur.execute(statement, (media_id,))
    res = res.fetchone()
    if res:
        return MediaItem(*res)

    return None


def get_user_borrowings(user_id: int) -> [Borrowing]:
    statement = """
        SELECT borrowings.id, media_id, user_id, borrow_date, return_date
        FROM borrowings
        JOIN users on borrowings.user_id = users.id
        WHERE users.id = ? AND return_date IS NULL
        """

    cur = con.cursor()
    res = cur.execute(statement, (user_id,))
    res = res.fetchall()

    return [Borrowing(*item) for item in res]


def get_borrowing(media_id: int, user_id: int) -> Borrowing:
    statement = """
        SELECT * 
        FROM borrowings
        WHERE media_id = ? AND user_id = ? 
        """

    cur = con.cursor()
    res = cur.execute(statement, (media_id, user_id))
    res = res.fetchone()
    if res:
        return Borrowing(*res)

    return None


def estimate_return_date(media_id: int) -> date | None:
    statement = """
        SELECT borrow_date, user_id
        FROM borrowings 
        WHERE media_id = ? AND return_date IS NULL
        """
    cur = con.cursor()
    res = cur.execute(statement, (media_id,))

    res = res.fetchone()

    if not res:
        return None

    borrow_date = datetime.strptime(res[0], "%Y-%m-%d")
    user_id = res[1]

    statement = """
        SELECT user_types.deadline 
        FROM users
        JOIN user_types ON users.user_type = user_types.id 
        WHERE users.id = ?
        """

    res = cur.execute(statement, (user_id,))
    res = res.fetchone()

    if res:
        days_until_deadline = res[0]
    else:
        days_until_deadline = 14

    deadline = borrow_date + timedelta(days=days_until_deadline)

    return deadline.date()


def borrow_book(media_id: int, user_id: int):
    statement = """
        INSERT INTO borrowings (media_id, user_id, borrow_date)
        VALUES (?, ?, ?)
        """

    today = date.today().__str__()

    cur = con.cursor()
    cur.execute(statement, (media_id, user_id, today))

    con.commit()


def return_media(borrowing_id: int, user_id: int):
    statement = """
        UPDATE borrowings
        SET return_date = ?
        WHERE id = ? AND user_id = ?
        """

    today = date.today().__str__()
    cur = con.cursor()
    cur.execute(statement, (today, borrowing_id, user_id))

    con.commit()


def update_user(user_id: int, attribute: str, value: str):
    statement = f"""
        UPDATE users
        SET {attribute} = ?
        WHERE id = ?
        """

    cur = con.cursor()
    cur.execute(statement, (value, user_id))

    con.commit()


def delete_user(user_id: int):
    for i in get_user_borrowings(user_id):
        return_media(i.id, user_id)

    statement = """
        DELETE FROM users
        WHERE users.id = ?
        """

    cur = con.cursor()
    cur.execute(statement, (user_id,))

    con.commit()
