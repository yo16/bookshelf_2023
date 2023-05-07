from flask_login import UserMixin
import hashlib


class DbMember(UserMixin):
    """member
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
    
    def to_string(self):
        s = f"id:{id}\n" + \
            f"org_id:{self.org_id}\n" + \
            f"member_id:{self.member_id}\n" + \
            f"password_hashed:{self.password_hashed}\n" + \
            f"member_name:{self.member_name}\n" + \
            f"member_code:{self.member_code}\n" + \
            f"is_admin:{self.is_admin}\n"
        
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
    def get(org_id, member_id, con):
        """org_id, member_idからユーザー情報を取得する

        Args:
            org_id (int): 組織ID
            member_id (int): メンバーID
        """
        # org_id、member_idがNoneの場合は、return None
        if ((not org_id) or (not member_id)):
            return None

        # PKだからあっても１件
        with con.cursor() as cur:
            db_password_hashed = None
            db_member_name = None
            db_member_code = None
            db_is_admin = None
            cur.execute(
                "select " + \
                "password_hashed, " + \
                "member_name, " + \
                "member_code, " + \
                "is_admin " + \
                "from member " + \
                f"where org_id={org_id} and member_id={member_id};")
            (password_hashed, member_name, member_code, is_admin) = cur.fetchone()
            db_password_hashed = password_hashed
            db_member_name = member_name
            db_member_code = member_code
            db_is_admin = is_admin

        # 取得出来たらDbMemberを作成
        member = None
        if db_password_hashed is not None:
            member = DbMember(
                org_id,
                member_id,
                db_password_hashed,
                db_member_name,
                db_member_code,
                db_is_admin
            )

        return member

    @staticmethod
    def get_member_id_by_member_code(org_id, member_code, con):
        ret_member_id = None

        with con.cursor() as cur:
            query = "select member_id from member " + \
                f"where org_id={org_id} and " + \
                f"member_code=\"{member_code}\";"
            cur.execute(query)
            ret = cur.fetchone()
            if (ret is not None):
                ret_member_id = ret[0]
        
        return ret_member_id
