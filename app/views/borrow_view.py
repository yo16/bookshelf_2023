from flask import redirect, url_for, request
from flask_login import current_user
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.sql.expression import and_

from models import get_db, DbBorrowedHistory
from .forms import BorrowBookForm


def main(app):
    borrow_form = BorrowBookForm(request.form)

    with get_db() as db:
        # 過去に借りた件数を取得
        borrow_times_past = db.scalars(
            select(DbBorrowedHistory.borrow_times).where(
                and_(
                    DbBorrowedHistory.org_id == current_user.org_id,
                    DbBorrowedHistory.member_id == current_user.member_id,
                    DbBorrowedHistory.book_id == borrow_form.book_id.data
                )
            )
        ).first()
        if borrow_times_past is None:
            borrow_times_past = 0

        his = DbBorrowedHistory(
            org_id = current_user.org_id,
            member_id = current_user.member_id,
            book_id = borrow_form.book_id.data,
            borrow_times = borrow_times_past + 1,
            borrow_dt = datetime.now()
        )
        db.add(his)
        db.commit()
        db.refresh(his)

    return redirect(url_for("book", book_id=borrow_form.book_id.data))

