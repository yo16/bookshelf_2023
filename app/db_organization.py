import random


class DbOrganization():
    def __init__(self, org_id, org_name):
        self.org_id = org_id
        self.org_name = org_name
    
    @staticmethod
    def get_free_org_id(con):
        """新しいorg_idのために、かぶらないorg_idを適当に決めて返す
        """
        with con.cursor() as cur:
            cur.execute("select count(*) from organization;")
            org_count = cur.fetchone()[0]
            # ２桁増やして作る
            keta_increment = 2
            len_count = len(str(org_count))

            already_exists = True
            while already_exists:
                # 新しい番号を発行
                new_org_id = random.randint(
                    10**(len_count+keta_increment),
                    10**(len_count+keta_increment+1)-1
                )
                print(f"new_org_id:{new_org_id}")
                # 存在しているか確認
                cur.execute(
                    f"select count(*) from organization where org_id={new_org_id};"
                )
                org_count = cur.fetchone()[0]
                print(f"count:{org_count}")
                if (org_count==0):
                    already_exists = False

        # 新しい番号を返す
        return new_org_id


