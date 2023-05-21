from flask_login import current_user
from flask import render_template
from sqlalchemy import select

from models import get_db, DbBook
from .view_common import get_org_mem


def main(app):
    org_mem = get_org_mem()

    return render_template("book.html", **org_mem)

