from flask import render_template, request, redirect, url_for
from sqlalchemy import update
from sqlalchemy.sql.expression import and_

from models import get_db, DbBook, DbCollection
from .view_common import get_org_mem
from .forms import EditBookForm, BorrowBookForm, ReturnBookForm


def main(app):
    edit_form = EditBookForm(request.form)
    borrow_form = BorrowBookForm(request.form)
    return_form = ReturnBookForm(request.form)

    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id
    book_id = request.args.get("book_id")
    message = request.args.get("msg")

    # 数の変更のための編集のPOSTがsubmitされた場合
    if edit_form.is_submitted():
        edit_book(org_id, book_id, int(request.form.get("num_of_same_books")))

    # 指定された本が組織に登録されているか確認しつつ本情報を取得
    book_info = DbBook.get_book_info(book_id, org_id)
    if book_info is None:
        # なかったらmainに飛ばす
        redirect(url_for("main"))
    edit_form.num_of_same_books.data = book_info["num_of_same_books"]
    borrow_form.book_id.data = book_id
    return_form.book_id.data = book_id

    return render_template(
        "book.html", **org_mem,
        book_info=book_info,
        message=message,
        edit_form=edit_form,
        borrow_form=borrow_form,
        return_form=return_form
    )


def edit_book(org_id, book_id, num_of_book):
    """本の情報を変更する
    現在は本の情報というか、collectionの本の数しかない。

    Args:
        org_id (int): org_id
        book_id (int): book_id
        num_of_book (int): 本の数
    """
    with get_db() as db:
        stmt = update(
            DbCollection
        ).values(
            num_of_same_books = num_of_book
        ).where(
            and_(
                DbCollection.org_id == org_id,
                DbCollection.book_id == book_id
            )
        )
        db.execute(stmt)
        db.commit()

