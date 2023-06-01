from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db_common import Base


class DbClassification(Base):
    __tablename__ = "classification"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(primary_key=True)
