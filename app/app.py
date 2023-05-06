# coding:utf-8
from flask import Flask, request, abort, redirect, url_for, render_template
import json
from flask_login import LoginManager, login_user, login_required

from app_logger import initialize_logger
from models import get_db_connection, DbOrganization, DbMember


# アプリケーション
app = Flask(__name__)
app.config.from_file("development.json", load=json.load, silent=True)

# ロガーを設定
initialize_logger(app.logger)

# ログインマネージャーを初期化
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ------ api ------

@app.route("/")
@login_required
def top():
    app.logger.info("hello world!")
    return "hello world!"


@app.route("/test", methods=["GET"])
def test():
    with get_db_connection(app) as con:
        with con.cursor() as cur:
            cur.execute("select count(*) from organization;")
            text = ""
            for cnt in cur:
                text += f"{cnt},"
    
    return "test ok!<br />" + text, 404


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        org_name = request.form["org_name"]
        member_code = request.form["member_code"]
        member_name = member_code
        password = request.form["password"]
        hashed_password = DbMember.hash_password(password)

        # 登録
        with get_db_connection(app) as db_con:
            new_org_id = DbOrganization.get_free_org_id(db_con)

            with db_con.cursor() as cur:
                query = f"insert into organization values ({new_org_id}, \"{org_name}\");"
                print(f"q:{query}")
                cur.execute(query)
                # member（初メンバーは、member_id=0、is_admin=True）
                query = "insert into member values (" + \
                    f"{new_org_id}, 0, \"{hashed_password}\", \"{member_name}\", \"{member_code}\", true)"
                print(f"q:{query}")
                cur.execute(query)
                # genre
                query = "insert into genre values(" + \
                    f"{new_org_id}, 0, NULL, \"分類なし\");"
                print(f"q:{query}")
                cur.execute(query)

                query = "commit;"
                print(f"q:{query}")
                cur.execute(query)
        message = f"組織ID={new_org_id}、メンバーID={member_code}を登録しました"

        return render_template(
            "login.html",
            error=message,
            org_id=new_org_id,
            member_code=member_code
        )

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        org_id = request.form["org_id"]
        member_code = request.form["member_code"]
        password = request.form["password"]

        # DBのmemberを取得
        with get_db_connection(app) as db_con:
            # member_codeからmember_idを取得
            member_id = DbMember.get_member_id_by_member_code(org_id, member_code, db_con)
            # DbMemberを作成
            db_user = DbMember.get(org_id, member_id, db_con)
            if db_user and db_user.verify_password(password):
                # 一致
                login_user(db_user)
                return redirect(url_for("top"))
        
        # 認証失敗
        error_message = "組織ID、ユーザー名、またはパスワードが正しくありません。"
        return render_template("login.html", error=error_message)
    
    return render_template("login.html")


@login_manager.user_loader
def load_user(id):
    splitted_id = id.split("-")
    org_id = splitted_id[0]
    member_id = splitted_id[1]
    member = None
    with get_db_connection(app) as con:
        member = DbMember.get(org_id, member_id, con)
    
    return member


if __name__=='__main__':
    app.run(host='0.0.0.0')
