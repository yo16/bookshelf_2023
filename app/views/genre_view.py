from flask import render_template

from models import get_db, DbGenre, DbClassification
from .view_common import get_org_mem


def main(app):
    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id

    genres = []
    with get_db() as db:
        # 登録されているgenre情報を取得
        genres = get_genre_info(db, org_id)

        # ジャンルごとの本の数
        genre_book_num = DbClassification.get_books_num_by_genres(db, org_id)

    # 描画
    return render_template(
        "genre.html",
        **org_mem,
        genres = genres,
        genre_book_num = genre_book_num,
        debug = False
    )


def get_genre_info(db, org_id):
    genres = DbGenre.get_genres(db, org_id)
    p_genres = DbGenre.pretty_genres(genres)
    return p_genres

