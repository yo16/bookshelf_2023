from flask import render_template, request
from sqlalchemy import select
import re

from models import get_db, DbGenre, DbClassification
from .view_common import get_org_mem
from .forms import RegistGenreForm, EditGenreForm, DeleteGenreForm, EditGenreOrderForm


def main(app):
    form = RegistGenreForm(request.form)
    regist_form = RegistGenreForm(request.form)
    regist_form.method.data = "POST"
    edit_form = EditGenreForm(request.form)
    edit_form.method.data = "PUT"
    edit_order_form = EditGenreOrderForm(request.form)
    edit_order_form.method.data = "PUT"
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
                delta = request.form.get("edit_order_delta")
                if (delta):
                    # edit2_sort_order_delta がある場合は位置の変更
                    edit_genre_order(db, org_id, request.form)
                    
                else:
                    # ない場合は項目の変更
                    # 編集（この関数内でget_dbしてcommitする）
                    edit_genre(db, org_id, request.form)

            elif (method=="DELETE"):
                # 削除（この関数内でget_dbしてcommitする）
                delete_genre(db, org_id, request.form)

            # フォームを初期化
            regist_form = RegistGenreForm()

        # 登録されているgenre情報を取得
        genres = get_genre_info(db, org_id)

        # ジャンルごとの本の数
        genre_book_num = DbClassification.get_books_num_by_genres(db, org_id)

    # 描画
    return render_template(
        "genre.html",
        **org_mem,
        regist_form = regist_form,
        edit_form = edit_form,
        edit_order_form = edit_order_form,
        delete_form = delete_form,
        genres = genres,
        genre_book_num = genre_book_num,
        debug = False
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

    # genre_id=0で作成するbook_id
    new_classification_book_ids = []

    # 削除対象のジャンルを持つclassificationを取得
    classes = DbClassification.get_classifications_with_genre(db, org_id, genre_id)
    if classes:
        # bookが今のgenre_idにしか登録されていない場合は、0のレコードを生成する
        for cur_cls in classes:
            registed_classes = DbClassification.get_classifications(db, org_id, cur_cls.book_id)
            if len(registed_classes) == 1: 
                # このgenre_idにしか登録されていないので、0のレコードを生成
                new_classification_book_ids.append(cur_cls.book_id)
    # classificationを削除
    DbClassification.delete_classification_by_genre(db, org_id, genre_id)

    # classificationを作成
    new_classifications = []
    for cur_book_id in new_classification_book_ids:
        new_classifications.append(
            DbClassification(
                org_id = org_id,
                genre_id = 0,           # ジャンル=0は、分類なし
                book_id = cur_book_id
            )
        )
    for c in new_classifications:
        db.add(c)

    # ジャンルを削除
    DbGenre.delete_genre(db, org_id, genre_id)

    # commit
    db.commit()
    
    for c in new_classifications:
        db.refresh(c)


def edit_genre_order(db, org_id, form):
    """登録情報からgenreを変更する（当関数内でcommitする）
    """
    # 順番を変える数
    order_delta = int(form.get("edit_order_delta"))
    # 方向（増える方向か減る方向か）
    delta_direction = 1 if order_delta > 0 else -1

    # 対象のジャンルID、ジャンル
    genre_id = form.get("edit_order_genre_id")
    cur_genre = DbGenre.get_genre(db, org_id, genre_id)

    # 親ジャンル
    parent_genre_id = cur_genre.parent_genre_id
    parent_genre = DbGenre.get_genre(db, org_id, parent_genre_id)

    # 同じ親を持つジャンルリスト（cur_genreを含む）
    genre_children = DbGenre.get_children(db, org_id, parent_genre_id)

    # 順番を変える元の位置を取得(sort_keyの値に無関係.削除すると飛び番が発生してしまうため.)
    old_pos_i = -1  # 元の位置
    for i, g_c in enumerate(genre_children):
        if g_c.genre_id == cur_genre.genre_id:
            old_pos_i = i
            break
    
    # 順番を変える先の位置
    new_pos_i = old_pos_i + order_delta     # 先の位置
    if new_pos_i < 0:
        new_pos_i = 0
    elif len(genre_children) <= new_pos_i:
        new_pos_i = len(genre_children) - 1

    # oldからnewに向かって１つずつ、sort_keyを交換していく
    for i in range(old_pos_i, new_pos_i, delta_direction):
        # genre_children（対象と同じレベル）と、その子のsort_keyを交換
        sort_key1 = genre_children[i].sort_key
        sort_key2 = genre_children[i+delta_direction].sort_key

        pattern_1 = r"^" + re.escape(sort_key1)
        pattern_2 = r"^" + re.escape(sort_key2)
        update_genre_sort_key(db, org_id, genre_children[i], pattern_1, sort_key2)     # 1→2
        update_genre_sort_key(db, org_id, genre_children[i+delta_direction], pattern_2, sort_key1)     # 2→1

        #genre_children[i].sort_key = genre_children[i+delta_direction].sort_key
        #genre_children[i+delta_direction].sort_key = tmp_sort_key

    # commit
    db.commit()
    for g in genre_children:
        db.refresh(g)


def update_genre_sort_key(db, org_id, top_genre, old_sort_pattern, new_sort_key_head):
    """ジャンルのトップと、それ以下のsort_keyをnew_sort_keyに変更する(再帰的に)

    Args:
        db (db): DB接続情報
        org_id (int): 組織ID
        top_genre (DbGenre): トップのジャンル
        old_sort_pattern (str): 置換元の正規表現パターン
        new_sort_key_head (str): 変更するsort_keyの先頭部分。パターンに一致する部分をこの文字列に置換する。
    """
    # 自分のsort_key
    old_sort_key = top_genre.sort_key
    
    # 自分のsort_keyを変更
    # old_sort_keyの先頭からnew_sort_keyと一致している部分を置換した文字列を取得
    new_sort_key = re.sub(old_sort_pattern, new_sort_key_head, old_sort_key)
    # トップのジャンルのsort_keyを変更(UPDATE)
    top_genre.sort_key = new_sort_key

    # 自分の配下のジャンルを変更
    # 同じ親を持つジャンルリスト（cur_genreを含む）
    genre_children = DbGenre.get_children(db, org_id, top_genre.genre_id)
    # 子のジャンルを順番に置換
    for g in genre_children:
        update_genre_sort_key(db, org_id, g, old_sort_pattern, new_sort_key_head)

    return
