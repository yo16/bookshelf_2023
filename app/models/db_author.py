from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .db_common import Base


class DbAuthor(Base):
    __tablename__ = "author"

    author_id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False)
