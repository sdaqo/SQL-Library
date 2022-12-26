from flask import Blueprint, session, redirect, request, send_from_directory

misc_bluep = Blueprint("misc_bluep", __name__, template_folder="templates")


@misc_bluep.route("/darkmode", methods=["GET"])
def toggle_darkmode():
    darkmode = session.get("darkmode", False)
    session["darkmode"] = not darkmode

    return redirect(request.args.get("next", "/"))


@misc_bluep.route("/gridtoggle", methods=["GET"])
def toggle_grid():
    grid = session.get("grid", True)
    session["grid"] = not grid
    
    return redirect(request.args.get("next", "/"))


@misc_bluep.route("/favicon.ico", methods=["GET"])
def get_favicon():
    return send_from_directory("static", "images/favicon.ico")
