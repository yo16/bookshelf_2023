from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbGenre
from .view_common import get_org_mem
from .forms import RegistGenreForm


def main(app):
    form = RegistGenreForm(request.form)
    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id

    genres = []
    with get_db() as db:
        if form.validate_on_submit():
            # 親のgenre情報から、今回のsort_keyを取得
            parent_genre = DbGenre.get_genre(db, org_id, int(request.form["parent_genre_id"]))
            new_sort_key = DbGenre.get_next_sort_key(db, parent_genre)

            # 登録（中でcommitする）
            regist_genre(db, org_id, new_sort_key)

            # フォームを初期化
            form = RegistGenreForm()

        # 登録されているgenre情報を取得
        genres = get_genre_info(db, org_id)

    # 描画
    return render_template(
        "genre.html",
        **org_mem,
        form = form,
        genres = genres
    )


def get_genre_info(db, org_id):
    genres = DbGenre.get_genres(db, org_id)
    p_genres = DbGenre.pretty_genres(genres)
    return p_genres


def regist_genre(db, org_id, new_sort_key):
    """登録情報からgenreを作成する（当関数内でcommitする）
    """
    genre = DbGenre(
        org_id = org_id,
        genre_id = DbGenre.get_new_genre_id(db, org_id),
        parent_genre_id = int(request.form["parent_genre_id"]),
        genre_name = request.form["genre_name"],
        sort_key = new_sort_key
    )

    db.add(genre)
    db.commit()
    db.refresh(genre)

    return
