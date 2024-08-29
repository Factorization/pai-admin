import argparse
import getpass
import sys

import sqlalchemy as sa
from email_validator import EmailNotValidError, validate_email
from tabulate import tabulate

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


def get_existing_user(app):
    valid = False
    while valid is not True:
        username = input("Username: ").strip().lower()
        with app.app_context():
            user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is not None:
            valid = True
        else:
            print("User does not exist. Please try again with a different username.")
            print()
    return user


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
        user.set_password(password)
        db.session.add(user)
        db.session.commit()


def main_create_user(app):
    username = get_username(app)
    email = get_email(app)
    password = get_password()
    create_user(username, email, password, app)
    print(f"User '{username}' - created successfully!")


def main_delete_user(app):
    user = get_existing_user(app)
    confirm = input("Are you sure you want to delete this user? [y|N]: ")
    if confirm.lower() == "y":
        with app.app_context():
            db.session.delete(user)
            db.session.commit()
            print(f"User '{user.username}' - deleted successfully!")
    else:
        print("User NOT deleted. Exiting...")


def main_set_password(app):
    user = get_existing_user(app)
    password = get_password()
    with app.app_context():
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"User '{user.username}' - password changed successfully!")


def main_list_users(app):
    with app.app_context():
        users = (
            db.session.execute(sa.select(User).order_by(User.username)).scalars().all()
        )
    results = [(user.username, user.email) for user in users]
    print()
    print(tabulate(results, headers=["Username", "Email"], tablefmt="rounded_outline"))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Flask Management Tools",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--create-user",
        action="store_true",
        help="Create new user",
        required=False,
    )
    parser.add_argument(
        "-d",
        "--delete-user",
        action="store_true",
        help="Delete user",
        required=False,
    )
    parser.add_argument(
        "-s",
        "--set-password",
        action="store_true",
        help="Set user password",
        required=False,
    )
    parser.add_argument(
        "-l", "--list-users", action="store_true", help="List users", required=False
    )
    return parser


if __name__ == "__main__":
    try:
        parser = parse_args()
        args = parser.parse_args()
        app = create_app()
        print()
        if args.create_user:
            print("-------------")
            print("Creating user")
            print("-------------")
            main_create_user(app)
        elif args.delete_user:
            print("-----------")
            print("Delete user")
            print("-----------")
            main_delete_user(app)
        elif args.set_password:
            print("---------------------")
            print("Setting user password")
            print("---------------------")
            main_set_password(app)
        elif args.list_users:
            print("-------------")
            print("Listing users")
            print("-------------")
            main_list_users(app)
        else:
            parser.print_help()
        print()

    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(-1)
