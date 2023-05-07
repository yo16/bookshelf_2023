from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column
import random

from .db_common import Base, get_db


class DbOrganization(Base):
    __tablename__ = "organization"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    org_name: Mapped[str] = mapped_column(String(100), nullable=False)


    @staticmethod
    def get_free_org_id():
        """新しいorg_idのために、かぶらないorg_idを適当に決めて返す
        """
        db = next(get_db())
        result = db.execute(select(DbOrganization)).scalars().all()
        count_all_org = len(result)

        # ２桁増やして作る
        keta_increment = 2
        count_keta = len(str(count_all_org))

        already_exists = True
        while already_exists:
            # 新しい番号を発行
            new_org_id = random.randint(
                10**(count_keta+keta_increment),
                10**(count_keta+keta_increment+1)-1
            )
            print(f"new_org_id:{new_org_id}")
            # 存在しているか確認
            result = db.execute(
                select(DbOrganization).where(DbOrganization.org_id == new_org_id)
            ).scalar()
            if (not result):    # 中身は関係なく存在していなければよし
                already_exists = False

        # 新しい番号を返す
        return new_org_id

