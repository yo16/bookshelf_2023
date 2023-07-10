from flask import redirect, url_for, request
from flask_login import current_user
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.sql.expression import and_

from models import get_db, DbBookNote
from .forms import NoteBookForm


def main(app):
    note_form = NoteBookForm(request.form)
    book_id = note_form.book_id.data
    note = note_form.note.data

    with get_db() as db:
        # 最後のnote_idを取得
        stmt = select(
            func.max(
                DbBookNote.note_id
            )
        ).select_from(
            DbBookNote
        )
        max_note_id = db.scalars(stmt).first()
        if max_note_id is None:
            max_note_id = 0

        note = DbBookNote(
            note_id = max_note_id + 1,
            org_id = current_user.org_id,
            member_id = current_user.member_id,
            book_id = book_id,
            noted_dt = datetime.now(),
            note = note,
        )
        db.add(note)
        db.commit()
        db.refresh(note)

    return redirect(url_for("books", book_id=book_id))

