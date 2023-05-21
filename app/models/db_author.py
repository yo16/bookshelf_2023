from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func

from .db_common import Base, get_db


class DbAuthor(Base):
    __tablename__ = "author"

    author_id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False)

    @staticmethod
    def get_new_author_id():
        new_author_id = 0

        db = next(get_db())
        result = db.execute(
            select(
                func.max(DbAuthor.author_id).label("max_author_id")
            )
        ).scalars().first()

        if result is None:
            new_author_id = 0
        else:
            new_author_id = result.max_author_id + 1
        
        return new_author_id
