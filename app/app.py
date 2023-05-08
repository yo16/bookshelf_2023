# coding:utf-8
from flask import Flask, request, abort, redirect, url_for, render_template
import json
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import flask_wtf
import wtforms

from app_logger import initialize_logger
from models import create_sqlalchemy_engine, get_db, DbOrganization, DbMember, DbGenre


# アプリケーション
app = Flask(__name__)
app.config.from_file("development.json", load=json.load, silent=True)

# ロガーを設定
initialize_logger(app.logger)

# ログインマネージャーを初期化
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ログインフォーム
class LoginForm(flask_wtf.FlaskForm):
    org_id = wtforms.IntegerField(
        'org_id',
        [wtforms.validators.DataRequired()]
    )
    member_code = wtforms.StringField(
        'member_code',
        [wtforms.validators.DataRequired()]
    )
    password = wtforms.PasswordField(
        'password',
        [
            wtforms.validators.DataRequired()
        ]
    )

# DB接続
create_sqlalchemy_engine(app)


# ------ api ------

# ****** login不要 ******
@app.route("/test", methods=["GET"])
def test():
    debug = app.config["DEBUG"]
    if not debug:
        return redirect(url_for("main"))
    
    from sqlalchemy import select
    db = next(get_db())
    #result = db.execute(select(DbOrganization)).scalars().all()
    result = db.execute(select(DbMember)).scalars().all()
    #count = result.count()
    #text = f"DbOrganization count:{count}"
    print(result)
    len_result = len(result)
    text = f"count:{len_result}"
    for c in result:
        print('----')
        print(c.org_id)

    return "test ok!<br />" + text, 404


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        org_name = request.form["org_name"]
        member_id = 0
        member_code = request.form["member_code"]
        member_name = member_code
        member_is_admin = True
        password = request.form["password"]
        hashed_password = DbMember.hash_password(password)
        genre_id = 0
        genre_name = "分類なし"
        parent_genre_id = None

        # 登録
        db = next(get_db())
        new_org_id = DbOrganization.get_free_org_id()

        # organization
        new_organization = DbOrganization(
            org_id = new_org_id,
            org_name = org_name
        )
        db.add(new_organization)

        # member
        new_member = DbMember(
            org_id = new_org_id,
            member_id = member_id,
            password_hashed = hashed_password,
            member_name = member_name,
            member_code = member_code,
            is_admin = member_is_admin,
            id = f"{new_org_id}-{member_id}"
        )
        db.add(new_member)

        # genre
        new_genre = DbGenre(
            org_id = new_org_id, 
            genre_id = genre_id,
            parent_genre_id = parent_genre_id,
            genre_name = genre_name
        )
        db.add(new_genre)

        db.commit()
        db.refresh(new_organization)
        db.refresh(new_member)
        db.refresh(new_genre)
        message = f"組織ID={new_org_id}、メンバーID={member_code}を登録しました"

        form = LoginForm(request.form)
        form.org_id.data = new_org_id
        form.member_code.data = member_code
        return redirect(url_for("login", message=message, org_id=new_org_id, member_code=member_code))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        org_id = form.org_id.data
        member_code = form.member_code.data
        password = form.password.data

        # memberを取得してログイン
        member_id = DbMember.get_member_id_by_member_code(org_id, member_code)
        member = DbMember.get(org_id, member_id)
        if member and member.verify_password(password):
            # 一致
            login_user(member)
            return redirect("main")
        
        # 認証失敗
        message = "組織ID、ユーザー名、またはパスワードが正しくありません。"
        return render_template("login.html", message=message, form=form)
    
    message = request.args.get('message')
    form.org_id.data = request.args.get('org_id')
    form.member_code.data = request.args.get('member_code')
    return render_template("login.html", form=form, message=message)


@app.errorhandler(404)
def page_not_found(error):
    # page not found時は何も言わず転送する
    return redirect(url_for("main"))


# ****** login必要（通常ユーザー） ******

@app.route("/")
@login_required
def main():
    app.logger.info("/")

    #print(current_user.to_string())

    return "hello world!"


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()

    form = LoginForm(request.form)
    message = "ログアウトしました"
    return redirect(url_for("login", message=message))


@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    return "book"


@app.route("/borrow", methods=["POST"])
@login_required
def borrow():
    return "borrow"



# ****** login必要（管理者ユーザー） ******

@app.route("/maintenance", methods=["GET"])
@login_required
def maintenance():
    # 管理者以外はbooksへ飛ばす
    if not current_user.is_admin:
        redirect(main"))

    return "maintenance"
 

@app.route("/export_books", methods=["POST"])
@login_required
def export_books():
    # 管理者以外はbooksへ飛ばす
    if not current_user.is_admin:
        redirect(url_for("main"))
    
    return "export_books"


@app.route("/regist_book", methods=["POST"])
@login_required
def regist_book():
    # 管理者以外はbooksへ飛ばす
    if not current_user.is_admin:
        redirect(url_for("main"))
    
    return "regist_book"


@app.route("/get_book_with_isbn", methods=["POST"])
@login_required
def get_book_with_isbn():
    # 管理者以外はbooksへ飛ばす
    if not current_user.is_admin:
        redirect(url_for("main"))
    
    return "get_book_with_isbn"


@app.route("/member", methods=["GET", "POST"])
@login_required
def member():
    # 管理者以外はbooksへ飛ばす
    if not current_user.is_admin:
        redirect(url_for("main"))
    
    return "member"


@app.route("/regist_member_with_csv", methods=["POST"])
@login_required
def regist_member_with_csv():
    # 管理者以外はbooksへ飛ばす
    if not current_user.is_admin:
        redirect(url_for("main"))
    
    return "regist_member_with_csv"


@login_manager.user_loader
def load_user(id):
    if id is None:
        return None

    splitted_id = id.split("-")
    org_id = splitted_id[0]
    member_id = splitted_id[1]
    member = DbMember.get(org_id, member_id)
    
    return member


if __name__=='__main__':
    app.run(host='0.0.0.0')
