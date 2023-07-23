from flask import redirect, url_for, request
from flask_login import current_user
from datetime import datetime
from sqlalchemy.sql.expression import and_
import re

from models import get_db, DbBookNote
from .forms import TakeANoteForm


def main(app):
    note_form = TakeANoteForm(request.form)
    book_id = note_form.book_id.data
    note = note_form.note.data
    
    # タグはエスケープ
    note = note.replace("<", "&lt;")
    note = note.replace(">", "&gt;")
    # 末尾の改行は削除
    note = note.replace("\r", "")   # \r\nの場合、\rを消す
    note = re.sub(r"\n+$", "", note)

    # note内の改行を<br />に置換
    str_note = note.replace("\n", "<br />")

    with get_db() as db:
        rec_note = DbBookNote.take_a_note(
            db,
            org_id = current_user.org_id,
            member_id = current_user.member_id,
            book_id = book_id,
            note = str_note,
        )
        
        db.add(rec_note)
        db.commit()
        db.refresh(rec_note)
        
    return redirect(url_for("books", book_id=book_id))
