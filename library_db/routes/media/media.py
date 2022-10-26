import re
from copy import deepcopy
from math import ceil
from flask import (
    Blueprint,
    session,
    redirect,
    render_template,
    request,
    abort,
    Response,
)


from library_db.utils.utils import get_template_vars, update_query_params, is_loggedin
from library_db.utils.db_utils import (
    get_media_list,
    is_media_borrowed,
    get_media_query_count,
    get_user_data,
    return_media,
)

media_bluep = Blueprint("media_bluep", __name__, template_folder="templates")

PAGE_SIZE = 20
AUTHOR_REGEX = r".*by\((.*)\).*"


def page_count(query_count):
    if query_count > PAGE_SIZE:
        return ceil(query_count / PAGE_SIZE)

    return 1


@media_bluep.route("/medialist", methods=["GET"])
def show_medialist():
    allowed_query_params = ["sort", "query", "media_type", "sort_type"]

    page = request.args.get("page", 0, type=int)
    query_params = {}
    for name, value in request.args.items():
        if name in allowed_query_params:
            query_params.update({name: value})

    table_data_prams = deepcopy(query_params)

    author_query_match = re.match(AUTHOR_REGEX, query_params.get("query", ""))
    if author_query_match:
        table_data_prams.update({"author_query": author_query_match.group(1)})
        table_data_prams["query"] = re.sub(AUTHOR_REGEX, "", table_data_prams["query"])
        table_data_prams["query"] = table_data_prams["query"].strip()

    query_count = get_media_query_count(
        table_data_prams.get("query", ""),
        table_data_prams.get("author_query", ""),
        table_data_prams.get("media_type", ""),
    )

    table_data = get_media_list(PAGE_SIZE, PAGE_SIZE * page, **table_data_prams)

    template_vars = get_template_vars(session)
    template_vars["table_data"] = table_data[0]
    template_vars["query"] = query_params.get("query", None)
    template_vars["media_type_selection"] = query_params.get("media_type", None)
    template_vars["sort_field"] = table_data[1]
    template_vars["sort_dir"] = table_data[2]
    template_vars["is_media_borrowed"] = is_media_borrowed
    template_vars["page"] = page
    template_vars["page_count"] = page_count(query_count)
    template_vars["page_size"] = PAGE_SIZE
    template_vars["url"] = request.url
    template_vars["update_query_params"] = update_query_params
    return render_template("media/medialist.html", **template_vars)


@media_bluep.route("/media/return", methods=["POST"])
def return_borrowed_media():
    if not is_loggedin(session):
        return redirect("/")

    if not request.form.get("borrowing_id"):
        return abort(Response("Bad Form Data", 400))

    borrowing_id = request.form["borrowing_id"]
    user_id = get_user_data(session.get("email")).get("id")

    return_media(borrowing_id, user_id)

    return redirect(request.args.get("next", "/"))
