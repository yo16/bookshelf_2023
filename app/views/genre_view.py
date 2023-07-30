from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbGenre
from .view_common import get_org_mem
from .forms import RegistGenreForm, EditGenreForm, DeleteGenreForm


def main(app):
    form = RegistGenreForm(request.form)
    regist_form = RegistGenreForm(request.form)
    regist_form.method.data = "POST"
    edit_form = EditGenreForm(request.form)
    edit_form.method.data = "PUT"
    delete_form = DeleteGenreForm(request.form)
    delete_form.method.data = "DELETE"

    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id

    genres = []
    with get_db() as db:
        # 本来は、methodを分けたいが、ブラウザが対応していないので
        # formの中身で分岐する
        if regist_form.validate_on_submit():
            method = request.form.get("method")
            if (method=="POST"):
                # 追加（中でcommitする）
                regist_genre(db, org_id, request.form)

            elif (method=="PUT"):
                # 編集（この関数内でget_dbしてcommitする）
                pass

            elif (method=="DELETE"):
                # 削除（この関数内でget_dbしてcommitする）
                pass

            # フォームを初期化
            regist_form = RegistGenreForm()

        # 登録されているgenre情報を取得
        genres = get_genre_info(db, org_id)

    # 描画
    return render_template(
        "genre.html",
        **org_mem,
        regist_form = regist_form,
        edit_form = edit_form,
        delete_form = delete_form,
        genres = genres,
        debug = True
    )


def get_genre_info(db, org_id):
    genres = DbGenre.get_genres(db, org_id)
    p_genres = DbGenre.pretty_genres(genres)
    return p_genres


def regist_genre(db, org_id, form):
    """登録情報からgenreを作成する（当関数内でcommitする）
    """
    # 親ジャンルID、親ジャンル情報
    parent_genre_id = int(form.get("reg_parent_genre_id"))
    parent_genre = DbGenre.get_genre(db, org_id, parent_genre_id)

    # 親のgenre情報から、今回のsort_keyを取得
    new_sort_key = DbGenre.get_next_sort_key(db, parent_genre)

    # ジャンル名
    new_genre_name = form.get("reg_genre_name")

    # 新しいgenreを作成
    genre = DbGenre(
        org_id = org_id,
        genre_id = DbGenre.get_new_genre_id(db, org_id),
        parent_genre_id = parent_genre_id,
        genre_name = new_genre_name,
        sort_key = new_sort_key
    )

    # 登録
    db.add(genre)
    db.commit()
    db.refresh(genre)

    return
