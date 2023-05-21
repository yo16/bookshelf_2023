from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func

from .db_common import Base, get_db


class DbGenre(Base):
    __tablename__ = "genre"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    parent_genre_id: Mapped[int] = mapped_column()
    genre_name: Mapped[str] = mapped_column(String(100), nullable=False)


    @staticmethod
    def get_genres(org_id):
        db = next(get_db())
        genres = db.execute(
            select(
                DbGenre
            ).where(
                DbGenre.org_id == org_id
            )
        ).scalars().all()
        return genres


    @staticmethod
    def pretty_genres(genres):
        """ジャンル配列を階層化する
        組織は１つに絞り込まれている前提

        Args:
            genres (list): DbGenreの配列
        Returns:
            (dict): トップからたどれる階層化した状態
        """
        def get_child_genres(parent_id):
            ret_genres = []
            for g in genres:
                if g.parent_genre_id == parent_id:
                    ret_genres.append({
                        "genre": g,
                        "children": get_child_genres(g.genre_id)
                    })
            return ret_genres
        
        if len(genres)==0:
            return {}

        # 組織が統一されていることを確認
        for i in range(1, len(genres)):
            assert(
                genres[0].org_id == genres[i].org_id,
                f"org_id is not unified!({genres[0].org_id}, {genres[i].org_id})"
            )

        # トップはparent_genre_id is NULLで、必ず１件だけ存在する
        top_genre = None
        for g in genres:
            if g.parent_genre_id == None:
                top_genre = g
                break
        assert(top_genre is not None)

        ret_obj = {
            "genre": g,
            "children": get_child_genres(g.genre_id)
        }

        return ret_obj


    @staticmethod
    def get_new_genre_id(org_id):
        new_genre_id = 0

        db = next(get_db())
        exec_result = db.execute(
            select(
                func.max(DbGenre.genre_id).label("max_book_id")
            ).where(
                DbGenre.org_id == org_id
            )
        )
        result = exec_result.scalars().first()
        
        if result is None:
            new_genre_id = 0
        else:
            new_genre_id = result + 1
        
        return new_genre_id