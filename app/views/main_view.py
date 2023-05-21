from flask_login import current_user
from flask import render_template
from sqlalchemy import select

from models import get_db, DbBook
from .view_common import get_org_mem


def main(app):
    org_mem = get_org_mem()

    books = DbBook.get_books_collection(org_mem["organization"].org_id)

    return render_template("main.html", **org_mem, books=books)
