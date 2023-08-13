from flask_login import current_user
from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbBook, DbGenre, DbAuthor, DbPublisher
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
        # 文字列の整備、int化
        search_str = None if ss is None or len(ss)==0 else ss
        genre_id = int(gn) if gn is not None else None
        author_id = int(au) if au is not None else None
        publisher_id = int(pb) if pb is not None else None

        # 検索条件で使っているIDを文字列に変換
        search_cond_str = None
        if search_str is not None:
            search_cond_str = f"検索:{search_str}"
        elif genre_id is not None:
            genre = DbGenre.get_genre(db, current_user.org_id, genre_id)
            search_cond_str = f"ジャンル:{genre.genre_name}"
        elif author_id is not None:
            author = DbAuthor.get_author(db, author_id)
            search_cond_str = f"著者:{author.author_name}"
        elif publisher_id is not None:
            publisher = DbPublisher.get_publisher(db, publisher_id)
            search_cond_str = f"出版者:{publisher.publisher_name}"

        books = DbBook.get_books_collection(
            db,
            org_mem["organization"].org_id,
            search_str=search_str,
            genre_id=genre_id,
            author_id=author_id,
            publisher_id=publisher_id
        )
    
    # booksの情報を整理
    book_info = []
    for bi in books:
        book_info.append({
            "book": bi[0],
            "authors": bi[1].split(","),
            "author_ids": bi[2].split(","),
        })

    return render_template(
        "main.html", **org_mem,
        books=book_info,
        search_str=ss,
        genre_id=genre_id,
        author_id=author_id,
        publisher_id=publisher_id,
        search_cond_str=search_cond_str
    )
