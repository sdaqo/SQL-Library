from hashlib import md5
from flask import Blueprint, abort, render_template, session, redirect, url_for, request


from library_db.utils.utils import is_admin, get_template_vars
from library_db.utils.db_utils import delete_user, get_user_data, update_user

admin_bluep = Blueprint("admin_bluep", __name__, template_folder="templates")


@admin_bluep.route("/", methods=["GET"])
def admin_panel():
    return redirect(url_for("panel_bluep.admin_bluep.user_managment"))


@admin_bluep.route("/users", methods=["GET"])
def user_managment():
    if not is_admin(session):
        return abort(403)

    template_vars = get_template_vars(session)
    template_vars["pw_user_error"] = request.args.get("pw_error")
    template_vars["del_user_error"] = request.args.get("del_error")
    return render_template("admin/user_mng.html", **template_vars)


@admin_bluep.route("/users/changepw", methods=["POST"])
def change_user_pw():
    if not is_admin(session):
        return abort(403)

    user = get_user_data(request.form.get("user", ""))
    if not user:
        return redirect(
            url_for("panel_bluep.admin_bluep.user_managment", pw_error="User not Found")
        )

    password = request.form.get("password")
    if not password:
        return redirect(
            url_for("panel_bluep.admin_bluep.user_managment", pw_error="Bad Form Data")
        )

    update_user(
        user.get("id"), attribute="pwdhash", value=md5(password.encode()).hexdigest()
    )

    return redirect(url_for("panel_bluep.admin_bluep.user_managment"))


@admin_bluep.route("/users/delete", methods=["POST"])
def del_user():
    if not is_admin(session):
        return abort(403)

    user = get_user_data(request.form.get("user", ""))
    if not user:
        return redirect(
            url_for(
                "panel_bluep.admin_bluep.user_managment", del_error="User not Found"
            )
        )

    delete_user(user.get("id"))
    return redirect(url_for("panel_bluep.admin_bluep.user_managment"))


@admin_bluep.route("/server", methods=["GET"])
def server_dashboard():
    if not is_admin(session):
        return abort(403)

    hostname, port = request.headers.get("Host").split(":")

    template_vars = get_template_vars(session)
    template_vars["hostname"] = hostname
    template_vars["port"] = port
    return render_template("admin/server_dash.html", **template_vars)
