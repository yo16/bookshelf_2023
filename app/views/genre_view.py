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
        if regist_form.is_submitted():
            method = request.form.get("method")
            if (method=="POST"):
                # 追加（中でcommitする）
                regist_genre(db, org_id, request.form)

            elif (method=="PUT"):
                # 編集（この関数内でget_dbしてcommitする）
                edit_genre(db, org_id, request.form)

            elif (method=="DELETE"):
                # 削除（この関数内でget_dbしてcommitする）
                delete_genre(db, org_id, request.form)

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


def edit_genre(db, org_id, form):
    """登録情報からgenreを編集する（当関数内でcommitする）
    """
    # 対象のジャンルID、ジャンル
    genre_id = form.get("edit_genre_id")
    cur_genre = DbGenre.get_genre(db, org_id, genre_id)

    # 変更項目
    # 親ジャンルID
    parent_genre_id = form.get("edit_parent_genre_id")
    # ジャンル名
    genre_name = form.get("edit_genre_name")

    # 変更
    cur_genre.parent_genre_id = parent_genre_id
    cur_genre.genre_name = genre_name

    # commit
    db.commit()
    db.refresh(cur_genre)


def delete_genre(db, org_id, form):
    """登録情報からgenreを削除する（当関数内でcommitする）
    """
    # 対象のジャンルID、ジャンル
    genre_id = form.get("del_genre_id")

    # 削除
    DbGenre.delete_genre(db, org_id, genre_id)

    # commit
    db.commit()
