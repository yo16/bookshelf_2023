from sqlalchemy import String, DateTime, select, func, asc, and_
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .db_common import Base
from . import DbMember


class DbBookNote(Base):
    __tablename__ = "book_note"

    note_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(nullable=False)
    member_id: Mapped[int] = mapped_column(nullable=False)
    book_id: Mapped[int] = mapped_column(nullable=False)
    noted_dt: Mapped[datetime]  = mapped_column(DateTime, nullable=False)
    note: Mapped[str]  = mapped_column(String(2000), nullable=False)

    @staticmethod
    def take_a_note(db, org_id, member_id, book_id, note):
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

        # 新規作成
        note = DbBookNote(
            note_id = max_note_id + 1,
            org_id = org_id,
            member_id = member_id,
            book_id = book_id,
            noted_dt = datetime.now(),
            note = note,
        )

        return note


    @staticmethod
    def get_notes(db, org_id, book_id):
        results = None

        # authors
        stmt = select(
            DbBookNote,
            DbMember
        ).join(
            target = DbMember,
            onclause = and_(
                DbMember.org_id == DbBookNote.org_id,
                DbMember.member_id == DbBookNote.member_id,
            )
        ).where(
            DbBookNote.org_id == org_id,
            DbBookNote.book_id == book_id
        ).order_by(
            asc(DbBookNote.noted_dt)
        )
        results = db.execute(stmt).all()
        if (results is None) or (len(results) == 0):
            # 存在しない場合は空の配列を返す
            return []
        
        return results
