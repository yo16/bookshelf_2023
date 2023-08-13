import datetime
from sqlalchemy import String, DateTime, select
from sqlalchemy.orm import Mapped, mapped_column, aliased
from sqlalchemy.sql.expression import func, asc, and_

from .db_common import Base
from .db_collection import DbCollection
from .db_author import DbAuthor
from .db_writing import DbWriting
from .db_publisher import DbPublisher
from .db_borrowed_history import DbBorrowedHistory
from .db_book_note import DbBookNote
from .db_member import DbMember
from .db_genre import DbGenre
from .db_classification import DbClassification


class DbBook(Base):
    __tablename__ = "book"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(50), unique=True)
    book_name: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[str] = mapped_column(String(150))
    publisher_id: Mapped[int] = mapped_column()
    published_dt: Mapped[datetime.datetime] = mapped_column(DateTime)
    page_count: Mapped[int] = mapped_column()
    dimensions_height: Mapped[int] = mapped_column()
    dimensions_width: Mapped[int] = mapped_column()
    dimensions_thickness: Mapped[int] = mapped_column()
    original_description: Mapped[str] = mapped_column(String(1000))

    @staticmethod
    def get_new_book_id(db):
        new_book_id = 0

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
    def get_book_by_isbn(db, isbn):
        """ISBNをキーに、本情報を取得する。ない場合はNoneを返す
        """
        exec_result = db.execute(
            select(DbBook).where(DbBook.isbn == isbn)
        ).scalar()
        if exec_result is None:
            return None
        
        # 結果を返す
        return exec_result


    @staticmethod
    def get_books_collection(db, org_id,
                             search_str=None, genre_id=None, author_id=None, publisher_id=None):
        """組織が持つ本一覧を返す

        Args:
            org_id (int): 組織id
            search_str (str): タイトル検索ワード（いつか著者もやるかも）
            genre_id (int): genre_id
            author_id (int): author_id
            publisher_id (int): publisher_id
        """
        # ベースのクエリ
        # 組織が所有する全book
        subq = select(
            DbCollection.book_id.label("book_id")
        ).where(
            DbCollection.org_id==org_id
        ).subquery()
        # group_concatで、名前とidの順序を一致してくれるかどうかは微妙
        stmt = select(
            DbBook,
            func.group_concat(DbAuthor.author_name),
            func.group_concat(DbAuthor.author_id),
        ).join(
            target = DbWriting,
            onclause = DbBook.book_id == DbWriting.book_id
        ).join(
            target = DbAuthor,
            onclause  = DbWriting.author_id == DbAuthor.author_id
        ).join(
            target = subq,
            onclause = DbBook.book_id == subq.c.book_id
        )

        # search_strが指定されているときは、book_nameをlike検索
        if search_str:
            stmt = stmt.where(
                DbBook.book_name.like(f"%{search_str}%")
            )
        # genre_idが指定されているときは、classificationのgenre_idを結合
        if genre_id is not None:
            subq_genre = select(
                DbClassification.book_id.label("book_id")
            ).where(
                DbClassification.org_id == org_id,
                DbClassification.genre_id == genre_id
            ).subquery()
            stmt = stmt.join(
                target = subq_genre,
                onclause = DbBook.book_id == subq_genre.c.book_id
            )
        # author_idが指定されているときは、writingのauthor_idを結合
        if author_id is not None:
            subq_writing = select(
                DbWriting.book_id.label("book_id")
            ).where(
                DbWriting.author_id == author_id
            ).subquery()
            stmt = stmt.join(
                target = subq_writing,
                onclause = DbBook.book_id == subq_writing.c.book_id
            )
        # publisher_idが指定されているときは、publisherのpublisher_idを結合
        #   ここは本当はbookの情報を見れば十分で結合しなくていいけど、
        #   将来的に、publisher_nameを見たくなるかもしれないから結合する実装
        if publisher_id is not None:
            subq_publisher = select(
                DbPublisher.publisher_id.label("publisher_id")
            ).where(
                DbPublisher.publisher_id == publisher_id
            ).subquery()
            stmt = stmt.join(
                target = subq_publisher,
                onclause = DbBook.publisher_id == subq_publisher.c.publisher_id
            )
        
        stmt = stmt.group_by(
            DbBook.book_id
        )
        
        # 検索実行
        exec_result = db.execute(stmt).all()
        if (exec_result is None) or (len(exec_result) == 0):
            return []
        
        return exec_result


    @staticmethod
    def get_book_info(db, book_id, org_id):
        """bookとその周辺のテーブルも全部取得してdictにして返す
        book, publisher, authorsは org_idに依存しない。
        collection, genres, histories, book_notesは依存する。
        book_idに対応するbookがない場合は、Noneを返す。
        org_idに依存するテーブルがない場合は、
        単一データのものはNone、複数データのものは空配列を返す。

        Args:
            book_id (_type_): book_id
            org_id (_type_): org_id
        """
        # ---- org_id に依存しない ----
        # book, publisher
        result = db.execute(
            select(
                DbBook,
                DbPublisher
            ).where(
                DbBook.book_id == book_id
            ).join(
                target = DbPublisher,
                onclause = DbBook.publisher_id == DbPublisher.publisher_id
            )
        ).first()
        if (result is None) or (len(result) == 0):
            # 正常であれば存在するはず
            return None
        book, publisher = result

        # authors
        subq_writing = select(
            DbWriting.author_id.label("author_id")
        ).where(
            DbWriting.book_id == book_id
        ).subquery()
        stmt_authors = select(
            DbAuthor
        ).join(
            target = subq_writing,
            onclause = DbAuthor.author_id == subq_writing.c.author_id
        )
        authors = db.scalars(stmt_authors).all()
        if (authors is None) or (len(authors) == 0):
            # 正常であれば存在するはず
            return None
        
        # ---- org_id に依存する ----
        # collection
        stmt = select(
            DbCollection
        ).where(
            and_(
                DbCollection.org_id == org_id,
                DbCollection.book_id == book_id
            )
        )
        collections = db.execute(stmt).first()
        if (collections is None) or (len(collections) == 0):
            # 組織に登録していない本の場合はNone
            collection = None
        else:
            collection = collections[0]
        
        # genres
        subq_cls = select(
            DbClassification.org_id.label("org_id"),
            DbClassification.genre_id.label("genre_id")
        ).where(
            and_(
                DbClassification.org_id == org_id,
                DbClassification.book_id == book_id
            )
        ).subquery()
        stmt_genres = select(
            DbGenre
        ).join(
            target = subq_cls,
            onclause = and_(
                DbGenre.org_id == subq_cls.c.org_id,
                DbGenre.genre_id == subq_cls.c.genre_id
            )
        )
        genres = db.scalars(stmt_genres).all()
        if (genres is None) or (len(genres) == 0):
            # 組織に登録していない本の場合は空配列
            genres = []

        # borrowed_his
        subq_his = select(
            DbBorrowedHistory
        ).where(
            and_(
                DbBorrowedHistory.org_id == org_id,
                DbBorrowedHistory.book_id == book_id
            )
        ).subquery()
        subq_his_alias = aliased(DbBorrowedHistory, subq_his, "his")
        stmt_members = select(
            DbMember,
            subq_his_alias
        ).join(
            target = subq_his_alias,
            onclause = and_(
                DbMember.org_id == subq_his_alias.org_id,
                DbMember.member_id == subq_his_alias.member_id
            )
        ).order_by(
            subq_his_alias.borrowed_dt
        )
        hiss_result = db.execute(stmt_members).all()
        hiss = []
        if (hiss_result is not None):
            for rslt in hiss_result:
                hiss.append({
                    "member": rslt[0],
                    "borrowed_history": rslt[1],
                })

        # book_note
        subq_note = select(
            DbBookNote
        ).where(
            and_(
                DbBookNote.org_id == org_id,
                DbBookNote.book_id == book_id
            )
        ).subquery()
        subq_note_alias = aliased(DbBookNote, subq_note, "note")
        stmt_note_members = select(
            DbMember,
            subq_note_alias
        ).join(
            target = subq_note_alias,
            onclause = and_(
                DbMember.org_id == subq_note_alias.org_id,
                DbMember.member_id == subq_note_alias.member_id
            )
        ).order_by(
            subq_note_alias.noted_dt
        )
        notes_result = db.execute(stmt_note_members).all()
        notes = []
        if (notes_result is not None):
            for rslt in notes_result:
                notes.append({
                    "member": rslt[0],
                    "book_note": rslt[1],
                })

        return {
            "book": book,
            "publisher": publisher,
            "authors": authors,
            "collection": collection,
            "genres": genres,
            "histories": hiss,
            "book_notes": notes,
        }


    @staticmethod
    def get_bookhis_by_member(db, org_id, member_id):
        subq_his = select(
            DbBorrowedHistory
        ).where(
            and_(
                DbBorrowedHistory.org_id == org_id,
                DbBorrowedHistory.member_id == member_id
            )
        ).subquery()
        subq_his_alias = aliased(DbBorrowedHistory, subq_his, "his")
        stmt_book_his = select(
            DbBook,
            subq_his_alias
        ).join(
            target = subq_his_alias,
            onclause = DbBook.book_id == subq_his_alias.book_id
        ).order_by(
            subq_his_alias.borrowed_dt
        )
        book_his_result = db.execute(stmt_book_his).all()
        hiss = []
        if (book_his_result is not None):
            for rslt in book_his_result:
                hiss.append({
                    "book": rslt[0],
                    "borrowed_history": rslt[1],
                })

        return hiss

    
    @staticmethod
    def get_notes_by_member(db, org_id, member_id):
        ret = []

        # authors
        stmt = select(
            DbBookNote,
            DbBook
        ).join(
            target = DbBook,
            onclause = 
                DbBook.book_id == DbBookNote.member_id
        ).where(
            DbBookNote.org_id == org_id,
            DbBookNote.member_id == member_id
        ).order_by(
            asc(DbBookNote.book_id),
            asc(DbBookNote.noted_dt)
        )
        results = db.execute(stmt).all()
        if (results is None) or (len(results) == 0):
            # 存在しない場合は空の配列を返す
            return []

        for rslt in results:
            ret.append({
                "book_note": rslt[0],
                "book": rslt[1],
            })
        
        return ret
