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
    site_prefix = current_app.config["SITE_PREFIX"]

    return render_template("main/main.html", site_prefix=site_prefix, **vm.to_dict())


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

    return render_template("main/_partials/container.html")


@bp.route("/container", methods=["POST"])
@login_required
def container_manage():
    return redirect(url_for("main.index"))
