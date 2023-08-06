from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func

from .db_common import Base


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
    def get_new_publisher_id(db):
        new_publisher_id = 0

        result = db.execute(
            select(
                func.max(DbPublisher.publisher_id).label("max_pub_id")
            )
        ).scalars().first()

        if result is None:
            new_publisher_id = 0
        else:
            new_publisher_id = result + 1

        return new_publisher_id
    

    @staticmethod
    def get_publisher(db, publisher_id):
        publisher = db.execute(
            select(
                DbPublisher
            ).where(
                DbPublisher.publisher_id == publisher_id
            )
        ).first()
        if publisher is None or len(publisher)==0:
            return None
        
        return publisher[0]


    @staticmethod
    def get_publisher_by_pubcode(db, publisher_code):
        result = db.execute(
            select(
                DbPublisher
            ).where(
                DbPublisher.publisher_code == publisher_code
            )
        ).scalars().first()
        
        if result is None:
            return None

        return result

