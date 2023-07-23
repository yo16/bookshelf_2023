from sqlalchemy import String, select, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func, and_
from functools import cmp_to_key

from .db_common import Base, get_db


class DbGenre(Base):
    __tablename__ = "genre"
    __table_args__ = (UniqueConstraint("org_id", "sort_key"),)

    org_id: Mapped[int] = mapped_column(primary_key=True)
    genre_id: Mapped[int] = mapped_column(primary_key=True)
    parent_genre_id: Mapped[int] = mapped_column()
    genre_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_key: Mapped[str] = mapped_column(String(100), nullable=False)


    @staticmethod
    def get_genre(org_id, genre_id):
        with get_db() as db:
            genres = db.scalars(
                select(
                    DbGenre
                ).where(
                    and_(
                        DbGenre.org_id == org_id,
                        DbGenre.genre_id == genre_id
                    )
                )
            ).first()
        return genres


    @staticmethod
    def get_genres(org_id):
        """ジャンル一覧を取得する
        単純にDB項目のsort_keyでorder_byしても諸事情でダメなので、
        sort_genres()を呼ぶ
        """
        # DBから抽出
        with get_db() as db:
            genres = db.execute(
                select(
                    DbGenre
                ).where(
                    DbGenre.org_id == org_id
                )
            ).scalars().all()
        
        # ソートキーでソート
        genres_sorted = DbGenre.sort_genres(genres)

        return genres_sorted


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

            # 取得
            ary_genres = []
            for g in genres:
                if g.parent_genre_id == parent_id:
                    ary_genres.append(g)
            
            # ソート
            ary_genres_sorted = DbGenre.sort_genres(ary_genres)

            # 結果配列に入れる
            for g in ary_genres_sorted:
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

        with get_db() as db:
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
    

    @staticmethod
    def get_next_sort_key(parent_genre):
        """親genreから、その子の次のsort_keyを取得する

        Args:
            parent_genre (DbGenre): 親genre
        """
        with get_db() as db:
            stmt = select(
                DbGenre
            ).where(
                DbGenre.parent_genre_id == parent_genre.genre_id
            )
            exec_result = db.scalars(stmt).all()
        
        # 見つからない場合は1、見つかった場合はmax+1
        ret_sort_key = ""
        if (exec_result is None) or (len(exec_result)==0):
            ret_sort_key = f"{parent_genre.sort_key}1_"
        else:
            # genreを降順ソートして最初（一番大きい数）をmaxとする
            sorted_genres = DbGenre.sort_genres(exec_result, ascend=False)
            max_sort_key = sorted_genres[0].get_sort_key_tail()
            next_sort_key = str(int(max_sort_key) + 1)
            ret_sort_key = f"{parent_genre.sort_key}{next_sort_key}_"

        return ret_sort_key


    @staticmethod
    def sort_genres(genre_array, ascend=True):
        """genre配列を昇順ソートして返す(非破壊)

        Args:
            genre_array (list): DbGenreの配列
            acsend (bool): Ture: 昇順, False: 降順
        """
        def compare_genre(a, b):
            """ genreの比較
            階層の浅い方から比較する
            aの方が小さい場合は-1、大きい場合は1を返す
            """
            # 数値の配列にする（最後は空が入っているので除外）
            a_sort_keys = [ int(s) for s in a.sort_key.split("_")[:-1]]
            b_sort_keys = [ int(s) for s in b.sort_key.split("_")[:-1]]

            # 浅い方の数に合わせる
            a_is_shallower = -1      # ここでついでに、浅い方を保存しておく
            loop_num = len(a_sort_keys)
            if (len(b_sort_keys) < len(a_sort_keys)):
                a_is_shallower = 1
                loop_num = len(b_sort_keys)
            
            # 浅い方から１階層ずつ比較
            # 途中で異なっている場合、その段階で小さい方が先
            for i in range(loop_num):
                if (a_sort_keys[i] < b_sort_keys[i]):
                    return -1
                elif (a_sort_keys[i] > b_sort_keys[i]):
                    return 1
            
            # （完全に一致していることはない前提で）
            # 浅い方の深さまでは一致しているので、
            # 浅い方が先
            return a_is_shallower
        
        return sorted(genre_array, key=cmp_to_key(compare_genre), reverse=not ascend)
    

    def get_sort_key_tail(self):
        """DbGenre.sort_keyの最後のキーを返す

        Args:
            self (DbGenre): 抽出するgenre
        Returns:
            str: ソートキーの最後の番号（文字列）
        """
        # 通常は末尾に"_"がついてるはずなので、除外する
        sk = self.sort_key.rstrip("_")

        # 末尾の"_"はない前提でsplitして最後の要素を返す
        keys = sk.split("_")
        return keys[len(keys)-1]
