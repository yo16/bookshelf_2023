from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func

from .db_common import Base, get_db


class DbBook(Base):
    __tablename__ = "book"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(50), unique=True)
    book_name: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[str] = mapped_column(String(150))
    publisher_id: Mapped[int] = mapped_column()

    @staticmethod
    def get_new_book_id():
        db = next(get_db())
        result = db.execute(
            select(
                func.max(DbBook.book_id).label("max_book_id")
            )
        ).scalars().first()
        
        return result.max_book_id + 1