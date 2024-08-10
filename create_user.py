import getpass
import sys

import sqlalchemy as sa
from email_validator import EmailNotValidError, validate_email

from app import create_app, db
from app.models import User

MINIMUM_PASSWORD_LENGTH = 12


def is_valid_username(username, app):
    with app.app_context():
        user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is not None:
        return False
    return True


def is_valid_email(email, app):
    try:
        email_validated = validate_email(email, check_deliverability=False)
        email = email_validated.normalized
    except EmailNotValidError:
        return False, "NotValid", None
    with app.app_context():
        user = db.session.scalar(sa.select(User).where(User.email == email))
    if user is not None:
        return False, "AlreadyExits", None
    return True, "NoErrors", email


def is_valid_password(password1, password2):
    if password1 != password2:
        return False, "NoMatch"
    if len(password1) < MINIMUM_PASSWORD_LENGTH:
        return False, "TooShort"
    return True, "NoErrors"


def get_username(app):
    valid = False
    while valid is not True:
        username = input("Username: ").strip().lower()
        valid = is_valid_username(username, app)
        if valid is not True:
            print(
                "Username already exists. Please try again with a different username."
            )
            print()
    return username


def get_email(app):
    valid = False
    while valid is not True:
        email = input("Email Address: ").strip().lower()
        valid, error, email = is_valid_email(email, app)
        if valid is not True:
            if error == "NotValid":
                print(
                    "Invalid email address. Please try again with a valid email address."
                )
                print()
            elif error == "AlreadyExits":
                print(
                    "Email address already exits. Please try again with a different email address."
                )
                print()
    return email


def get_password():
    valid = False
    while valid is not True:
        password1 = getpass.getpass("Password: ").strip()
        password2 = getpass.getpass("Password (again): ").strip()
        valid, error = is_valid_password(password1, password2)
        if valid is not True:
            if error == "NoMatch":
                print("Passwords do not match. Please enter the password again.")
                print()
            if error == "TooShort":
                print(
                    f"Password does not meet the minimum length of {MINIMUM_PASSWORD_LENGTH}. Please try again with a longer password."
                )
                print()
    return password1


def create_user(username, email, password, app):
    with app.app_context():
        user = User(username=username, email=email)
        print(user)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


def main():
    app = create_app()
    username = get_username(app)
    email = get_email(app)
    password = get_password()

    create_user(username, email, password, app)
    print(f"User '{username}', created successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(-1)
