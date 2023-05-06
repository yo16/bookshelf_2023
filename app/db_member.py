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
    

    def verify_password(self, password):
        """ハッシュ化前のパスワードと、変数のself.password_hashedを比較する
        ハッシュ化の手法はこのクラスの責任なので、ここでハッシュ化する

        Returns:
            True: 一致, False: 不一致
        """
        password_hashed = DbMember.hash_password(password)
        return self.password_hashed == password_hashed


    @staticmethod
    def hash_password(password):
        hasher = hashlib.sha3_512()
        hasher.update(password.encode('utf-8'))
        password_hashed = hasher.hexdigest()
        return password_hashed


    @staticmethod
    def get(org_id, member_id, con):
        """idからユーザー情報を取得する

        Args:
            org_id (_type_): 組織ID
            member_id (_type_): メンバーID
        """
        # PKだからあっても１件
        with con.cursor() as cur:
            cur.execute(
                "select " + \
                "password_hashed, " + \
                "member_name, " + \
                "member_code, " + \
                "is_admin " + \
                "from member " + \
                f"where org_id={org_id} and member_id={member_id};")
            db_password_hashed = None
            db_member_name = None
            db_member_code = None
            db_is_admin = None
            for (password_hashed, member_name, member_code, is_admin) in cur:
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
