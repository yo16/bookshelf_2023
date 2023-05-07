from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db_common import Base


class DbGenre(Base):
    __tablename__ = "genre"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    parent_genre_id: Mapped[int] = mapped_column()
    genre_name: Mapped[str] = mapped_column(String(100), nullable=False)
