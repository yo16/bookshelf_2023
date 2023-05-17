from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func

from .db_common import Base, get_db


class DbPublisher(Base):
    __tablename__ = "publisher"

    publisher_id: Mapped[int] = mapped_column(primary_key=True)
    publisher_name: Mapped[str] = mapped_column(String(50), nullable=False)
    publisher_code: Mapped[str] = mapped_column(String(10), nullable=False)

    @staticmethod
    def get_publisher_code_from_isbn(isbn):
        """ 出版社コードを抜き出して返す
        """
        top2 = int(isbn[4:6])
        keta = 2
        if top2 < 20:
            keta = 2
        elif top2 < 70:
            keta = 3
        elif top2 < 85:
            keta = 4
        elif top2 < 90:
            keta = 5
        elif top2 < 95:
            keta = 6
        else:
            keta = 7
        return isbn[4:4+keta]


    @staticmethod
    def get_new_publisher_id():
        db = next(get_db())
        result = db.execute(
            select(
                func.max(DbPublisher.publisher_id).label("max_pub_id")
            )
        ).scalars().first()

        return result.max_pub_id
