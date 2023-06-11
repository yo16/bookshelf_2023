from flask import redirect, url_for, request
from flask_login import current_user
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.sql.expression import and_

from models import get_db, DbBorrowedHistory, DbCollection
from .forms import BorrowBookForm


def main(app):
    borrow_form = BorrowBookForm(request.form)
    book_id = borrow_form.book_id.data
    msg = ""

    with get_db() as db:
        # すでに借りられている件数を取得
        stmt = select(
            func.count(
                DbBorrowedHistory.book_id
            )
        ).select_from(
            DbBorrowedHistory
        ).where(
            and_(
                DbBorrowedHistory.org_id == current_user.org_id,
                DbBorrowedHistory.book_id == book_id,
                DbBorrowedHistory.returned_dt.is_(None)
            )
        )
        count_borrowed = db.scalars(stmt).first()
        if count_borrowed is None:
            count_borrowed = 0

        # 本の所有数を取得
        stmt = select(
            DbCollection.num_of_same_books
        ).where(
            and_(
                DbCollection.org_id == current_user.org_id,
                DbCollection.book_id == book_id,
            )
        )
        num_of_books_in_org = db.scalars(stmt).first()

        # 残っている本の数
        num_of_books_in_stock = num_of_books_in_org - count_borrowed
        
        if (num_of_books_in_stock > 0):
            # 残(所有数 - すでに借りられている件数) > 0 なら借りる処理

            # 過去に借りた件数を取得
            borrow_times_past = db.scalars(
                select(DbBorrowedHistory.borrow_times).where(
                    and_(
                        DbBorrowedHistory.org_id == current_user.org_id,
                        DbBorrowedHistory.member_id == current_user.member_id,
                        DbBorrowedHistory.book_id == book_id
                    )
                )
            ).first()
            if borrow_times_past is None:
                borrow_times_past = 0

            his = DbBorrowedHistory(
                org_id = current_user.org_id,
                member_id = current_user.member_id,
                book_id = book_id,
                borrow_times = borrow_times_past + 1,
                borrowed_dt = datetime.now()
            )
            db.add(his)
            db.commit()
            db.refresh(his)
        else:
            # 残がない場合は、エラーメッセージを返す
            msg = "すべて貸し出されており、残ってる本がありません。"

    return redirect(url_for("books", book_id=book_id, msg=msg))

