from flask import render_template, request, redirect, url_for
from sqlalchemy import select, update, func
from sqlalchemy.sql.expression import and_

from models import get_db, DbBook, DbCollection, DbBorrowedHistory, DbBookNote
from .view_common import get_org_mem
from .forms import EditBookForm, BorrowBookForm, ReturnBookForm, TakeANoteForm


def main(app, book_id):
    edit_form = EditBookForm(request.form)
    borrow_form = BorrowBookForm(request.form)
    return_form = ReturnBookForm(request.form)
    note_form = TakeANoteForm(request.form)

    if book_id is None:
        # book_idが指定されていなかったらmainに飛ばす
        return redirect(url_for("main"))

    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id
    message = request.args.get("msg")

    # 編集のPOSTがsubmitされた場合
    if edit_form.is_submitted():
        try:
            description = request.form.get("description", None)
            str_num_of_sb = request.form.get("num_of_same_books", None)
            edit_book(org_id, book_id, description, str_num_of_sb)
        except Exception as e:
            # num_of_book < count_borrowedのケース
            # DB更新はされていない
            message = "借りられている数より小さな値にすることはできません"

    # 指定された本が組織に登録されているか確認しつつ本情報を取得
    book_info = DbBook.get_book_info(book_id, org_id)
    if book_info is None:
        # なかったらmainに飛ばす
        return redirect(url_for("main"))
    edit_form.description.data = book_info["collection"].description
    edit_form.num_of_same_books.data = book_info["collection"].num_of_same_books
    edit_form.num_of_same_books.render_kw = {"style": "width: 50px; text-align: right"}
    borrow_form.book_id.data = book_id
    return_form.book_id.data = book_id
    note_form.book_id.data = book_id
    # コメント
    notes = DbBookNote.get_notes(org_id, book_id)

    return render_template(
        "books.html",
        **org_mem,
        book_info   = book_info,
        notes       = notes,
        message     = message,
        edit_form   = edit_form,
        borrow_form = borrow_form,
        return_form = return_form,
        note_form   = note_form,
    )


def edit_book(org_id, book_id, description, str_num_of_book):
    """本の情報を変更する

    Args:
        org_id (int): org_id
        book_id (int): book_id
        description (str): 概要
        str_num_of_book (str): 本の数
    """
    update_items = {}

    with get_db() as db:
        # num_of_book
        if str_num_of_book:
            num_of_book = int(str_num_of_book)

            # 現在借りられている数
            stmt = select(
                func.count(
                    DbBorrowedHistory.book_id
                )
            ).select_from(
                DbBorrowedHistory
            ).where(
                and_(
                    DbBorrowedHistory.org_id == org_id,
                    DbBorrowedHistory.book_id == book_id,
                    DbBorrowedHistory.returned_dt.is_(None)
                )
            )
            count_borrowed = db.scalars(stmt).first()
            if count_borrowed is None:
                count_borrowed = 0

            # この数より小さい値にしようとしている場合はエラー
            if (num_of_book < count_borrowed):
                raise Exception("num_of_book < count_borrowed")
            
            # 更新する項目を追加
            update_items["num_of_same_books"] = num_of_book
        
        # description
        if description:
            # 更新する項目を追加
            update_items["description"] = description
        
        # update実行
        stmt = update(
            DbCollection
        ).values(
            **update_items
        ).where(
            and_(
                DbCollection.org_id == org_id,
                DbCollection.book_id == book_id
            )
        )
        db.execute(stmt)

        # commit
        db.commit()

