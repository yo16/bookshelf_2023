from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, aliased
from sqlalchemy.sql.expression import func, and_

from .db_common import Base, get_db
from .db_collection import DbCollection
from .db_author import DbAuthor
from .db_writing import DbWriting
from .db_publisher import DbPublisher
from .db_genre import DbGenre
from .db_borrowed_history import DbBorrowedHistory
from .db_member import DbMember


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
    def get_book(book_id, org_id):
        """book_idをキーに、本情報を取得する。
        ない場合はNoneを返す。
        DBの構造上、org_idは指定しなくてもいいが、
        ロジック上、org_idが一致しないbook_idを取得することはないため、必ず指定することとする。
        """
        books = None
        num_of_same_books = 0
        with get_db() as db:
            subq = select(
                DbCollection.book_id.label("book_id")
            ).where(
                DbCollection.org_id == org_id
            ).subquery()
            stmt = select(
                    DbBook
                ).join(
                    target = subq,
                    onclause = DbBook.book_id == subq.c.book_id
                ).where(
                    DbBook.book_id == book_id
                )
            books = db.scalars(stmt).all()
            if (books is None) or (len(books) == 0):
                return None, 0
            # 見つかった場合は１件のはず
            assert(len(books)==1)

            # collectionをもう一度検索して、所有数を取得する
            # 本当は１発で取りたい・・・！
            stmt = select(
                DbCollection.num_of_same_books
            ).where(
                and_(
                    DbCollection.org_id == org_id,
                    DbCollection.book_id == book_id
                )
            )
            num_of_same_books = db.scalars(stmt).first()

        # 結果を返す
        return books[0], num_of_same_books


    @staticmethod
    def get_book_by_isbn(isbn):
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


    @staticmethod
    def get_book_info(book_id, org_id):
        """bookとその周辺のテーブルも全部取得してdictにして返す
        ない場合はNoneを返す。

        Args:
            book_id (_type_): book_id
            org_id (_type_): org_id
        """
        with get_db() as db:
            # book, publisher, collection
            subq_collection = select(
                DbCollection.book_id.label("book_id"),
                DbCollection.num_of_same_books.label("num_of_same_books")
            ).where(
                and_(
                    DbCollection.org_id == org_id,
                    DbCollection.book_id == book_id
                )
            ).subquery()
            result = db.execute(
                select(
                    DbBook,
                    DbPublisher.publisher_name,
                    subq_collection.c.num_of_same_books
                ).where(
                    DbBook.book_id == book_id
                ).join(
                    target = DbPublisher,
                    onclause = DbBook.publisher_id == DbPublisher.publisher_id
                ).join(
                    target = subq_collection,
                    onclause = DbBook.book_id == subq_collection.c.book_id
                )
            ).first()
            if (result is None) or (len(result) == 0):
                return None
            book = result[0]
            publisher_name = result[1]
            num_of_same_books = result[2]

            # authors
            subq_writing = select(
                DbWriting.author_id.label("author_id")
            ).where(
                DbWriting.book_id == book_id
            ).subquery()
            stmt_authors = select(
                DbAuthor.author_name.label("author_name")
            ).join(
                target = subq_writing,
                onclause = DbAuthor.author_id == subq_writing.c.author_id
            )
            authors = db.scalars(stmt_authors).all()
            if (authors is None) or (len(authors) == 0):
                return None

        return {
            "book": book,
            "num_of_same_books": num_of_same_books,
            "publisher": publisher_name,
            "authors": authors
        }

