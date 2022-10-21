import re
from flask import Blueprint, session, redirect, render_template, request, url_for
from copy import deepcopy

from library_db.utils.utils import get_template_vars
from library_db.database import get_db_connection
from library_db.utils.db_utils import get_media_list, is_media_borrowed

media_bluep = Blueprint("media_bluep", __name__, template_folder="templates")
con = get_db_connection()

PAGE_SIZE = 30
AUTHOR_REGEX = r".*by\((.*)\).*"


@media_bluep.route("/medialist", methods=["GET"])
def show_medialist():
    #TODO: PAGINATION
    allowed_query_params = ["sort", "query", "media_type", "sort_type"]

    query_params = {}
    for name, value in request.args.items():
        if name in allowed_query_params:
            query_params.update({name: value})

    table_data_prams = deepcopy(query_params)
    next_query_params = {
        "query": query_params.get("query", None),
        "media_type": query_params.get("media_type", None),
    }

    author_query_match = re.match(AUTHOR_REGEX, query_params.get("query", ""))
    if author_query_match:
        table_data_prams.update({"author_query": author_query_match.group(1)})
        table_data_prams["query"] = re.sub(AUTHOR_REGEX, "", table_data_prams["query"])
        table_data_prams["query"] = table_data_prams["query"].strip()

    table_data = get_media_list(10, 0, **table_data_prams)
    template_vars = get_template_vars(session)
    template_vars["table_data"] = table_data[0]
    template_vars["query"] = query_params.get("query", None)
    template_vars["media_type_selection"] = query_params.get("media_type", None)
    template_vars["sort_field"] = table_data[1]
    template_vars["sort_dir"] = table_data[2]
    template_vars["next_query_params"] = next_query_params
    template_vars["is_media_borrowed"] = is_media_borrowed

    return render_template("media/medialist.html", **template_vars)


