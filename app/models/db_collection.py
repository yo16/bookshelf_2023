from sqlalchemy import DateTime, select, and_
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .db_common import Base, get_db


class DbCollection(Base):
    __tablename__ = "collection"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(primary_key=True)
    num_of_same_books: Mapped[int] = mapped_column(nullable=False)
    added_dt: Mapped[datetime]  = mapped_column(DateTime, nullable=False)

    @staticmethod
    def get_collection(org_id, book_id):
        """組織IDとbook_idをキーに、collection情報を取得する。
        ない場合はNoneを返す。

        Args:
            org_id (int): 組織ID
            book_id (int): 本ID
        """
        db = next(get_db())
        exec_result = db.execute(
            select(DbCollection).where(
                and_(
                    DbCollection.org_id == org_id,
                    DbCollection.book_id == book_id
                )
            )
        ).scalar()
        if exec_result is None:
            return None
        
        # 結果を返す
        return exec_result
