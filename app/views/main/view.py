import os
from datetime import timedelta

from flask import (
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.bin.utils import log_request
from app.models import File, get_all_files
from app.services.container import Container
from app.services.index import IndexFile
from app.viewmodels.main.main_viewmodel import MainViewModel
from app.views.main import bp


@bp.before_request
def before_request():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(hours=2)
    session.modified = True
    g.user = current_user


@bp.route("/", methods=["GET"])
@login_required
def index():
    log_request()
    vm = MainViewModel()

    return render_template("main/main.html", **vm.to_dict())


@bp.route("/file/<int:id>/delete", methods=["Delete"])
@login_required
def delete_file(id):
    log_request()

    file = db.get_or_404(File, id)
    file.delete_file()
    return ""


@bp.route("/upload", methods=["GET"])
@login_required
def upload_modal():
    log_request()
    supported_extensions = [
        f".{extension.removeprefix('.')}"
        for extension in current_app.config["SUPPORTED_FILE_EXTENSIONS"]
    ]
    return render_template(
        "main/_partials/upload.html", supported_extensions=supported_extensions
    )


@bp.route("/upload", methods=["POST"])
@login_required
def upload_files():
    log_request()
    supported_extensions = {
        f".{extension.removeprefix('.')}"
        for extension in current_app.config["SUPPORTED_FILE_EXTENSIONS"]
    }
    uploaded_files = request.files.getlist("file")
    existing_files_names = [file.name for file in get_all_files()]
    for file in uploaded_files:
        filename = secure_filename(file.filename)  # type: ignore
        if filename != "":
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in supported_extensions:
                flash(f"Error: Unsupported file type for file '{filename}'.", "danger")
                continue
            if filename in existing_files_names:
                flash(
                    f"File '{filename}' already exists in directory. Please delete the existing file if you want to replace it.",
                    "warning",
                )
                continue
            file.save(os.path.join(current_app.config["DATA_DIR"], filename))
            flash(f"File '{filename}' uploaded successfully.", "success")
    return redirect(url_for("main.index"))


@bp.route("/container", methods=["GET"])
@login_required
def container_modal():
    log_request()
    container_minimum_uptime = current_app.config["MINIMUM_CONTAINER_UPTIME_SECONDS"]
    index_minimum_uptime = current_app.config["MINIMUM_INDEX_UPTIME_SECONDS"]
    return render_template(
        "main/_partials/container.html",
        container_name=current_app.config["CONTAINER_NAME"],
        container_minimum_uptime=container_minimum_uptime,
        index_minimum_uptime=index_minimum_uptime,
    )


@bp.route("/container/restartable", methods=["GET"])
@login_required
def is_container_restartable():
    log_request()
    container = Container(name=current_app.config["CONTAINER_NAME"])
    index = IndexFile(
        running_file_path=current_app.config["INDEX_RUNNING_FILE"],
        complete_file_path=current_app.config["INDEX_COMPLETE_FILE"],
    )
    container_restartable = container.is_restartable(
        must_be_up_for_seconds=current_app.config["MINIMUM_CONTAINER_UPTIME_SECONDS"]
    )
    index_restartable = index.is_restartable(
        must_be_up_for_seconds=current_app.config["MINIMUM_INDEX_UPTIME_SECONDS"]
    )
    print(container_restartable, index_restartable)
    if container_restartable and index_restartable:
        return render_template("main/_partials/container_restart_enabled.html")
    elif container_restartable and not index_restartable:
        button_text = "Waiting for index to complete..."
        return render_template(
            "main/_partials/container_restart_disabled.html", button_text=button_text
        )
    else:
        button_text = "Waiting for container to start..."
        return render_template(
            "main/_partials/container_restart_disabled.html", button_text=button_text
        )


@bp.route("/container/restart", methods=["POST"])
@login_required
def container_restart():
    log_request()
    container = Container(name=current_app.config["CONTAINER_NAME"])
    index = IndexFile(
        running_file_path=current_app.config["INDEX_RUNNING_FILE"],
        complete_file_path=current_app.config["INDEX_COMPLETE_FILE"],
    )
    container_restartable = container.is_restartable(
        must_be_up_for_seconds=current_app.config["MINIMUM_CONTAINER_UPTIME_SECONDS"]
    )
    index_restartable = index.is_restartable(
        must_be_up_for_seconds=current_app.config["MINIMUM_INDEX_UPTIME_SECONDS"]
    )
    if container_restartable and index_restartable:
        index.delete_index_complete_flag()
        container.restart(
            must_be_up_for_seconds=current_app.config[
                "MINIMUM_CONTAINER_UPTIME_SECONDS"
            ]
        )
    return render_template("main/_partials/container_restart_disabled.html")


@bp.route("/container/status", methods=["GET"])
@login_required
def container_status():
    log_request()
    container = Container(name=current_app.config["CONTAINER_NAME"])
    return render_template(
        "main/_partials/container_status.html", container_status=container.status
    )


@bp.route("/container/uptime", methods=["GET"])
@login_required
def container_uptime():
    log_request()
    container = Container(name=current_app.config["CONTAINER_NAME"])
    return render_template(
        "main/_partials/container_uptime.html",
        container_uptime=container.uptime[1],
    )


@bp.route("/container/index-status", methods=["GET"])
@login_required
def container_index_status():
    log_request()
    index = IndexFile(
        running_file_path=current_app.config["INDEX_RUNNING_FILE"],
        complete_file_path=current_app.config["INDEX_COMPLETE_FILE"],
    )
    if index.is_running():
        status = f"Running ({index.running_status()[1]})"
    elif index.is_complete():
        status = f"Complete ({index.complete_status()[1]})"
    else:
        status = "Unknown"
    return render_template(
        "main/_partials/container_index.html",
        index_status=status,
    )
