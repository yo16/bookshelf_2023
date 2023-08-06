from flask_login import current_user
from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbBook
from .view_common import get_org_mem


def main(app):
    org_mem = get_org_mem()

    books = []
    with get_db() as db:
        # GETパラメータを取得
        ss = request.args.get('ss', None)   # フリーテキスト
        gn = request.args.get('gn', None)   # genre_id
        au = request.args.get('au', None)   # author_id
        pb = request.args.get('pb', None)   # publisher_id

        books = DbBook.get_books_collection(
            db,
            org_mem["organization"].org_id,
            search_str=ss,
            genre_id=int(gn) if gn else None,
            author_id=int(au) if au else None,
            publisher_id=int(pb) if pb else None
        )

    return render_template("main.html", **org_mem, books=books)
