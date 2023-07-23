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

    with get_db() as db:
        # 指定された本が組織に登録されているか確認しつつ本情報を取得
        book_info = DbBook.get_book_info(db, book_id, org_id)
        if book_info is None:
            # なかったらmainに飛ばす
            return redirect(url_for("main"))
        borrow_form.book_id.data = book_id
        return_form.book_id.data = book_id
        note_form.book_id.data = book_id
        # コメント
        notes = DbBookNote.get_notes(db, org_id, book_id)

    # 貸出中の数
    borrowing_num = 0
    for his_and_member in book_info["histories"]:
        his = his_and_member["borrowed_history"]
        if his.returned_dt is None:
            borrowing_num += 1

    return render_template(
        "books.html",
        **org_mem,
        book_info       = book_info,
        notes           = notes,
        borrowing_num   = borrowing_num,
        remained_num    = book_info["collection"].num_of_same_books - borrowing_num,
        message         = message,
        borrow_form     = borrow_form,
        return_form     = return_form,
        note_form       = note_form,
    )


