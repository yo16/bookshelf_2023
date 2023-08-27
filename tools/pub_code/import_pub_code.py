# bookshelf_2023とは別の環境で実施
import sqlite3
import json

from db_common import create_sqlalchemy_engine, get_db
from db_publisher import DbPublisher


def import_pub_code(mysql_connect_info, sqlite_db_path, select_rec_num):
    # MySQLの初期処理
    create_sqlalchemy_engine(mysql_connect_info)

    # pub_codeのdb(SQLite)を読みながらmysqlにinsert
    # SQLiteへ接続
    with sqlite3.connect(sqlite_db_path, isolation_level=None) as conn_sqlite:  # 自動commit
        cur_sqlite = conn_sqlite.cursor()
        cur_sqlite.execute(
            "SELECT pub_code, pub_name FROM pub"
        )

        # MySQLへ接続
        with get_db() as db_mysql:
            # SQLiteから取得
            recs = cur_sqlite.fetchmany(select_rec_num)
            
            times = 0
            while len(recs):
                base_num = times * select_rec_num
                if base_num % 10000==0:
                    print(base_num)

                # MySQLにバルクインサート
                db_mysql.bulk_save_objects(
                    [
                        DbPublisher(
                            publisher_id=i + base_num,
                            publisher_code=rec[0],
                            publisher_name=rec[1] if rec[1] is not None else f"code[{rec[1]}]",
                        )
                        for i, rec in enumerate(recs)
                    ],
                    return_defaults=True
                )

                # MySQLへCommit
                db_mysql.commit()

                # SQLiteから再抽出
                recs = cur_sqlite.fetchmany(select_rec_num)
                times += 1


if __name__=='__main__':
    # bookshelfのdb(mysql)
    # 接続情報が書いてあるjsonファイル
    mysql_connect_info_file_path = "./app/development.json"
    mysql_connect_info = None
    with open(mysql_connect_info_file_path, mode="r") as f:
        mysql_connect_info = json.load(f)
    # ローカルで動かすために、設定を上書き
    mysql_connect_info["DBHOST"] = "127.0.0.1"
    mysql_connect_info["DEBUG"] = False

    # SQLiteのDBファイルパス
    sqlite_db_path  = "./tools/pub_code/pub_code_20230730_2.db"

    # １回で抽出するレコード件数
    select_rec_num = 1000


    # SQLite → MySQL
    import_pub_code(mysql_connect_info, sqlite_db_path, select_rec_num)
