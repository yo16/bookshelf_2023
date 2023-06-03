from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .db_common import Base


class DbBorrowedHistory(Base):
    __tablename__ = "borrowed_history"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(primary_key=True)
    borrow_times: Mapped[int] = mapped_column(primary_key=True)
    borrow_dt: Mapped[datetime]  = mapped_column(DateTime, nullable=False)
    returned_dt: Mapped[datetime]  = mapped_column(DateTime, nullable=True)
    note: Mapped[str] = mapped_column(String)
