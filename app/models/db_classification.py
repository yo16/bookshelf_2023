from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import and_

from .db_common import Base, get_db


class DbClassification(Base):
    __tablename__ = "classification"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(primary_key=True)

    @staticmethod
    def get_classifications(org_id, book_id):
        """指定した本に関するclassificationを全部取得

        Args:
            org_id (_type_): org_id
            book_id (_type_): book_id
        """
        with get_db() as db:
            classes = db.scalars(
                select(
                    DbClassification
                ).where(
                    and_(
                        DbClassification.org_id == org_id,
                        DbClassification.book_id == book_id
                    )
                )
            ).all()

        return classes
