from flask_login import UserMixin
from sqlalchemy import String, Boolean, UniqueConstraint, select, and_
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.expression import func, and_
import hashlib

from .db_common import Base


class DbMember(Base, UserMixin):
    __tablename__ = "member"
    __table_args__ = (UniqueConstraint("org_id", "member_code", name="uk_member_org_id_member_code"),)

    # id: UserMixinで使用するためのIDで、テーブルには持たないためmapped_columnにしない
    org_id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(primary_key=True)
    password_hashed: Mapped[str] = mapped_column(String(512), nullable=False)
    member_name: Mapped[str] = mapped_column(String(100), nullable=False)
    member_code: Mapped[str] = mapped_column(String(20), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    id = None

    """
    def __init__(self, org_id, member_id, password_hashed, member_name, member_code, is_admin):
        # UserMixinで使用するためのID
        self.id = str(org_id) + "-" + str(member_id)

        self.org_id = org_id
        self.member_id = member_id
        self.password_hashed = password_hashed
        self.member_name = member_name
        self.member_code = member_code
        self.is_admin = is_admin
        self.is_enabled = is_enabled
    """

    def to_string(self):
        s = f"id:{id}\n" + \
            f"org_id:{self.org_id}\n" + \
            f"member_id:{self.member_id}\n" + \
            f"password_hashed:{self.password_hashed}\n" + \
            f"member_name:{self.member_name}\n" + \
            f"member_code:{self.member_code}\n" + \
            f"is_admin:{self.is_admin}\n" + \
            f"is_enabled:{self.is_enabled}\n"
        
        return s


    @staticmethod
    def hash_password(password):
        """パスワードをハッシュ化
        """
        hasher = hashlib.sha3_512()
        hasher.update(password.encode('utf-8'))
        password_hashed = hasher.hexdigest()
        return password_hashed


    def verify_password(self, password):
        """ハッシュ化前のパスワードと、変数のself.password_hashedを比較する

        Returns:
            True: 一致, False: 不一致
        """
        password_hashed = DbMember.hash_password(password)
        return self.password_hashed == password_hashed


    @staticmethod
    def get(db, org_id, member_id):
        """org_id, member_idからユーザー情報を取得する

        Args:
            org_id (int): 組織ID
            member_id (int): メンバーID
        """
        # org_id、member_idがNoneの場合は、return None
        if ((org_id is None) or (member_id is None)):
            return None

        member = db.execute(
            select(
                DbMember
            ).where(
                and_(
                    DbMember.org_id == org_id,
                    DbMember.member_id == member_id
                )
            )
        ).scalars().first()
        if member is None:
            return None

        member.id = f"{org_id}-{member_id}"

        return member


    @staticmethod
    def get_members_in_org(db, org_id):
        members = db.scalars(
            select(
                DbMember
            ).where(
                DbMember.org_id == org_id
            )
        ).all()
        # 今この要求を出しているユーザーが必ず１人はいるはず
        assert(members is not None, "メンバーが見つからない")

        return members


    @staticmethod
    def get_member_id_by_member_code(db, org_id, member_code):
        member = db.execute(select(DbMember).where(
            and_(
                DbMember.org_id == org_id,
                DbMember.member_code == member_code
            )
        )).scalars().first()
        if member is None:
            return None
            
        ret_member_id = member.member_id
        
        return ret_member_id


    @staticmethod
    def get_new_member_id(db, org_id):
        new_member_id = 0

        exec_result = db.execute(
            select(
                func.max(DbMember.member_id).label("max_member_id")
            ).where(
                DbMember.org_id == org_id
            )
        )
        result = exec_result.scalars().first()
        
        if result is None:
            new_member_id = 0
        else:
            new_member_id = result + 1
        
        return new_member_id