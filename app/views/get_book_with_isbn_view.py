from flask_login import current_user
from flask import jsonify, request
from sqlalchemy import select
import json

from models import get_db, DbBook, DbWriting, DbAuthor, DbPublisher

def main(app):
    """自分のDBを見に行って、なかったらGoogleAPIで検索する
    """
    isbn = request.json['isbn']

    ret_dic = {
        'isbn': '',
        'title': '',
        'authors': [],
        'publisher': '',
        'publisher_code': '',
        'image_url': '',
        'comment': '',
        'tags': []
    }

    db = next(get_db())
    cur_book = db.execute(
        select(DbBook).where(DbBook.isbn == isbn)
    ).scalars().first()

    if cur_book:
        # 見つかったので関連情報を取得
        authors = []
        cur_authors = db.execute(
            select(DbWriting).where(DbWriting.book_id == cur_book.book_id)
        ).scalars().all()
        for cur_author in cur_authors:
            db.execute()

    else:
        # 見つからなかったので、Googleに問い合わせる
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&country=JP"
        print(f"URL:{url}")

    return jsonify(ResultSet=json.dumps(ret_dic))
