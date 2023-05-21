from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbGenre
from .view_common import get_org_mem
from .forms import RegistGenreForm


def main(app):
    form = RegistGenreForm(request.form)
    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id

    if form.validate_on_submit():
        # 登録
        regist_genre(org_id)

        # フォームを初期化
        form = RegistGenreForm()

    # 登録されているgenre情報を取得
    genres = get_genre_info(org_id)

    # 描画
    return render_template(
        "genre.html",
        **org_mem,
        form = form,
        genres = genres
    )


def get_genre_info(org_id):
    genres = DbGenre.get_genres(org_id)
    p_genres = DbGenre.pretty_genres(genres)
    return p_genres


def regist_genre(org_id):
    """登録情報からgenreを作成する
    """
    db = next(get_db())

    genre = DbGenre(
        org_id = org_id,
        genre_id = DbGenre.get_new_genre_id(org_id),
        parent_genre_id = int(request.form["parent_genre_id"]),
        genre_name = request.form["genre_name"]
    )

    db.add(genre)
    db.commit()
    db.refresh(genre)

    return
