from flask import redirect, url_for, request
from flask_login import current_user
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.sql.expression import and_

from models import get_db, DbBorrowedHistory
from .forms import ReturnBookForm


def main(app):
    return_form = ReturnBookForm(request.form)
    book_id = return_form.book_id.data
    note = return_form.note.data

    with get_db() as db:
        # 過去に借りた件数を取得
        stmt = select(
            DbBorrowedHistory
        ).where(
            and_(
                DbBorrowedHistory.org_id == current_user.org_id,
                DbBorrowedHistory.member_id == current_user.member_id,
                DbBorrowedHistory.book_id == book_id,
                DbBorrowedHistory.returned_dt.is_(None)
            )
        )
        borrow_times_past = db.scalars(stmt)
        if ((borrow_times_past is None) or (borrow_times_past.first() is None)):
            # 借りていない！
            message = "借りた履歴がありません"
            return redirect(url_for("book", book_id=book_id, msg=message))

        stmt = update(
            DbBorrowedHistory
        ).values(
            returned_dt = datetime.now(),
            note = note
        ).where(
            and_(
                DbBorrowedHistory.org_id == current_user.org_id,
                DbBorrowedHistory.member_id == current_user.member_id,
                DbBorrowedHistory.book_id == book_id,
                DbBorrowedHistory.returned_dt.is_(None)
            )
        )
        db.execute(stmt)
        db.commit()

    return redirect(url_for("book", book_id=book_id))

