from sqlalchemy import String, DateTime, select, and_
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .db_common import Base, get_db


class DbCollection(Base):
    __tablename__ = "collection"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(primary_key=True)
    num_of_same_books: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    added_dt: Mapped[datetime]  = mapped_column(DateTime, nullable=False)

    @staticmethod
    def get_collection(org_id, book_id=None):
        """組織IDとbook_idをキーに、collection情報を取得する。
        book_idの指定がない場合は、組織のみで抽出。
        ない場合は[]を返す。

        Args:
            org_id (int): 組織ID
            book_id (int): 本ID
        Reutrns:
            list: DbCollectionリスト
        """
        where_clause = None
        if book_id is None:
            where_clause = DbCollection.org_id == org_id,
        else:
            where_clause = and_(
                DbCollection.org_id == org_id,
                DbCollection.book_id == book_id
            )
        stmt = select(DbCollection).where(where_clause)

        with get_db() as db:
            collections = db.scalars(stmt).all()
        if (collections is None) or (len(collections) == 0):
            return []
        
        # 結果を返す
        return collections
