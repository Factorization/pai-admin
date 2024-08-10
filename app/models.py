import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):  # type: ignore
    __tablename__ = "user"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # type: ignore


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class File(db.Model):  # type: ignore
    __tablename__ = "file"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(200), index=True, unique=True)
    full_name: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(250), index=True, unique=True
    )
    extension: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(10), index=True, unique=False
    )
    size: so.Mapped[Optional[int]]
    upload_date: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<File {self.name}>"

    def set_fullname(self):
        basedir = current_app.config["DATA_DIR"]
        self.full_name = os.path.join(basedir, self.name)

    def delete_file(self):
        current_app.logger.info(f"Deleting file '{self.name}' from DB and directory.")
        if current_app.config["DELETE_FILE_ENABLED"]:
            Path(self.full_name).unlink(missing_ok=True)  # type: ignore
        db.session.delete(self)
        db.session.commit()


def get_all_files():
    return db.session.execute(sa.select(File).order_by(File.name)).scalars().all()
