from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db_common import Base


class DbWriting(Base):
    __tablename__ = "writing"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(primary_key=True)
