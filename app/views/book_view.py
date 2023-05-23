from flask_login import current_user
from flask import render_template, request, redirect, url_for
from sqlalchemy import select

from models import get_db, DbBook, DbCollection
from .view_common import get_org_mem
from .forms import EditBookForm, BorrowBookForm


def main(app):
    edit_form = EditBookForm(request.form)
    borrow_form = BorrowBookForm(request.form)

    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id
    book_id = request.args.get("book_id")

    # 指定された本が組織に登録されているか確認しつつ本情報を取得
    book, num_of_same_books = DbBook.get_book(book_id, org_id)
    if book is None:
        # なかったらmainに飛ばす
        redirect(url_for("main"))
    edit_form.num_of_same_books.data = num_of_same_books
    borrow_form.book_id.data = book_id

    return render_template(
        "book.html", **org_mem,
        book=book,
        edit_form=edit_form,
        borrow_form=borrow_form
    )

