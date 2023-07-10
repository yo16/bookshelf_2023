from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import and_

from .db_common import Base, get_db


class DbBookNote(Base):
    __tablename__ = "book_note"

    note_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(nullable=False)
    member_id: Mapped[int] = mapped_column(nullable=False)
    book_id: Mapped[int] = mapped_column(nullable=False)
    noted_dt: Mapped[datetime]  = mapped_column(DateTime, nullable=False)
    note: Mapped[str]  = mapped_column(String(2000), nullable=False)

