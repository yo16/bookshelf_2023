from sqlalchemy import select, delete, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import and_

from .db_common import Base, get_db


class DbClassification(Base):
    __tablename__ = "classification"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(primary_key=True)

    @staticmethod
    def get_classifications(db, org_id, book_id):
        """指定した本に関するclassificationを全部取得

        Args:
            org_id (_type_): org_id
            book_id (_type_): book_id
        """
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


    @staticmethod
    def get_books_num_by_genres(db, org_id):
        """ジャンルIDごとの本の数を返す

        Args:
            db (_type_): DB
            org_id (_type_): 組織ID
        """
        stmt = select(
            DbClassification.genre_id,
            func.count(
                DbClassification.book_id
            )
        ).select_from(
            DbClassification
        ).where(
            DbClassification.org_id == org_id,
        ).group_by(
            DbClassification.genre_id
        )
        count_books = db.execute(stmt).all()

        # genre_idをキー、本の数を値としたdictを作る
        ret = {}
        for cb in count_books:
            ret[cb[0]] = cb[1]

        return ret


    @staticmethod
    def get_classifications_with_genre(db, org_id, genre_id):
        """genre_idをキーにclassificationを返す

        Args:
            db (_type_): db
            org_id (_type_): org_id
            genre_id (_type_): genre_id
        """
        classes = db.scalars(
            select(
                DbClassification
            ).where(
                and_(
                    DbClassification.org_id == org_id,
                    DbClassification.genre_id == genre_id
                )
            )
        ).all()

        if (classes is None) or (len(classes)==0):
            return None

        return classes


    @staticmethod
    def delete_classification_by_genre(db, org_id, genre_id):
        """ジャンルID指定で削除

        Args:
            db (_type_): _description_
            org_id (_type_): _description_
            genre_id (_type_): _description_
        """
        db.execute(
            delete(
                DbClassification
            ).where(
                and_(
                    DbClassification.org_id == org_id,
                    DbClassification.genre_id == genre_id
                )
            )
        )

        return

