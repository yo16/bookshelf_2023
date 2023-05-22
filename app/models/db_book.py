from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func

from .db_common import Base, get_db
from .db_collection import DbCollection


class DbBook(Base):
    __tablename__ = "book"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(50), unique=True)
    book_name: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[str] = mapped_column(String(150))
    publisher_id: Mapped[int] = mapped_column()

    @staticmethod
    def get_new_book_id():
        new_book_id = 0

        with get_db() as db:
            exec_result = db.execute(
                select(
                    func.max(DbBook.book_id).label("max_book_id")
                )
            )
        result = exec_result.scalars().first()
        
        if result is None:
            new_book_id = 0
        else:
            new_book_id = result + 1
        
        return new_book_id

    @staticmethod
    def get_book(isbn):
        """ISBNをキーに、本情報を取得する。ない場合はNoneを返す
        """
        with get_db() as db:
            exec_result = db.execute(
                select(DbBook).where(DbBook.isbn == isbn)
            ).scalar()
        if exec_result is None:
            return None
        
        # 結果を返す
        return exec_result

    @staticmethod
    def get_books_collection(org_id):
        """組織が持つ本一覧を返す

        Args:
            org_id (int): 組織id
        """
        with get_db() as db:
            subq = select(
                DbCollection.book_id.label("book_id")
            ).where(DbCollection.org_id==org_id).subquery()
            stmt = select(DbBook).join(
                    target = subq,
                    onclause = DbBook.book_id == subq.c.book_id
                )
            exec_result = db.scalars(stmt).all()
        if (exec_result is None) or (len(exec_result) == 0):
            return []
        
        return exec_result
