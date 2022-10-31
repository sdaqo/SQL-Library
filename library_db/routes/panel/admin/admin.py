from hashlib import md5
from pathlib import Path
from flask import (
    Blueprint,
    abort,
    render_template,
    session,
    redirect,
    url_for,
    request,
    current_app,
    send_from_directory,
)


from library_db.utils.utils import is_admin, get_template_vars
from library_db.utils.db_utils import delete_user, get_user_data, update_user
from library_db.logger import (
    tfh_has_request_filter,
    RequestFilter,
    get_info_logfile,
    get_error_logfile,
)

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

    info_log_dir = Path(get_info_logfile()).parent
    error_log_dir = Path(get_error_logfile()).parent

    info_logs = [f.name for f in info_log_dir.iterdir() if not f.is_dir()]
    error_logs = [f.name for f in error_log_dir.iterdir() if not f.is_dir()]

    template_vars = get_template_vars(session)
    template_vars["hostname"] = hostname
    template_vars["port"] = port
    template_vars["has_filter"] = tfh_has_request_filter()
    template_vars["info_logs"] = info_logs
    template_vars["error_logs"] = error_logs
    return render_template("admin/server_dash.html", **template_vars)


@admin_bluep.route("/server/logs/info/<log>", methods=["GET"])
def get_info_log(log):
    if not is_admin(session):
        return abort(403)

    info_log_dir = Path(get_info_logfile()).parent
    log_file = info_log_dir / log

    if log_file.exists():
        return send_from_directory(directory=info_log_dir, path=log, as_attachment=True)

    return abort(404)


@admin_bluep.route("/server/logs/error/<log>", methods=["GET"])
def get_error_log(log):
    if not is_admin(session):
        return abort(403)

    error_log_dir = Path(get_error_logfile()).parent
    log_file = error_log_dir / log

    if log_file.exists():
        return send_from_directory(
            directory=error_log_dir, path=log, as_attachment=True
        )
    
    return abort(404)


@admin_bluep.route("/server/log/request_filter", methods=["POST"])
def toggel_request_filter():
    if not is_admin(session):
        return abort(403)

    time_file_handler = current_app.logger.handlers[0]

    if tfh_has_request_filter():
        time_file_handler.filters.pop(1)
    else:
        time_file_handler.addFilter(RequestFilter())

    return redirect(url_for("panel_bluep.admin_bluep.server_dashboard"))
