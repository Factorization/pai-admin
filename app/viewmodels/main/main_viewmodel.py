from pathlib import Path

import arrow
import sqlalchemy as sa
from flask import current_app

from app import db
from app.models import File
from app.viewmodels.shared.viewmodelbase import ViewModelBase


class MainViewModel(ViewModelBase):
    def __init__(self):
        super().__init__()
        self.load_files_to_db()
        self.files = self.get_files()

        self.flash_error()

    def load_files_to_db(self):
        current_app.logger.info("Loading files to DB...")

        supported_extensions = {
            f".{extension.removeprefix('.')}"
            for extension in current_app.config["SUPPORTED_FILE_EXTENSIONS"]
        }
        data_directory = Path(current_app.config["DATA_DIR"])
        data_directory_files = (
            file.resolve()
            for file in data_directory.glob("*")
            if file.suffix in supported_extensions
        )
        data_directory_file_names = []
        for file in data_directory_files:
            name = file.name
            data_directory_file_names.append(name)
            existing_file = db.session.scalar(sa.select(File).where(File.name == name))
            if existing_file is None:
                current_app.logger.info(f"Creating DB entry for file '{file.name}'")
                size = file.stat().st_size
                extension = file.suffix
                new_file = File(name=name, extension=extension, size=size)
                new_file.set_fullname()
                db.session.add(new_file)
                db.session.commit()
        db_files = (
            db.session.execute(sa.select(File).order_by(File.name)).scalars().all()
        )
        db_file_to_remove = [
            file for file in db_files if file.name not in data_directory_file_names
        ]
        for file in db_file_to_remove:
            current_app.logger.info(f"Removing file '{file.name}' from DB as it is no longer in the directory")
            db.session.delete(file)
            db.session.commit()

    def get_files(self):
        files = db.session.execute(sa.select(File).order_by(File.name)).scalars().all()
        for file in files:
            file.friendly_upload_date = arrow.get(file.upload_date).humanize()  # type: ignore
        return files
