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
        # 過去に借りた情報を取得
        stmt = select(
            DbBorrowedHistory
        ).where(
            and_(
                DbBorrowedHistory.org_id == current_user.org_id,
                DbBorrowedHistory.member_id == current_user.member_id,
                DbBorrowedHistory.book_id == book_id,
                DbBorrowedHistory.returned_dt.is_(None)
            )
        ).order_by(
            DbBorrowedHistory.borrow_times
        )
        borrow_times_past = db.scalars(stmt)
        oldest_his = None   # 借りている中で一番古い情報
        no_borrow = False
        if (borrow_times_past is None):
            no_borrow = True
        else:
            oldest_his = borrow_times_past.first()
            if (oldest_his is None):
                no_borrow = True
        if no_borrow:
            # 借りていない！
            message = "借りた履歴がありません"
            return redirect(url_for("books", book_id=book_id, msg=message))

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
                DbBorrowedHistory.returned_dt.is_(None),
                DbBorrowedHistory.borrow_times == oldest_his.borrow_times
            )
        )
        db.execute(stmt)
        db.commit()

    return redirect(url_for("books", book_id=book_id))

