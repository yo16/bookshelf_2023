# coding:utf-8
from flask import Flask, request, abort, redirect, url_for, render_template
import json
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps

from app_logger import initialize_logger
from models import create_sqlalchemy_engine, get_db, DbOrganization, DbMember, DbGenre
from views.main_view import main as main_view_main
from views.book_view import main as book_view_main
from views.borrow_view import main as borrow_view_main
from views.maintenance_view import main as maintenance_view_main
from views.member_view import main as member_view_main
from views.get_book_with_isbn_view import main as get_book_with_isbn_view_main
from views.signup_view import main as signup_view_main
from views.login_view import main as login_view_main
from views.logout_view import main as logout_view_main
from views.regist_book_view import main as regist_book_main
from views.export_books_view import main as export_books_view_main
from views.regist_member_with_csv_view import main as regist_member_with_csv_view_main
from views.test_view import main as test_view_main


# アプリケーション
app = Flask(__name__)
app.config.from_file("development.json", load=json.load, silent=True)

# ロガーを設定
initialize_logger(app.logger)

def log_info(func):
    @wraps(func)
    def wrapper(*args, **keywords):
        app.logger.info(func.__name__)
        return func(*args, **keywords)
    return wrapper


# ログインマネージャーを初期化
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# DB接続
create_sqlalchemy_engine(app)


# ------ api ------

# ****** login不要 ******
@app.route("/test", methods=["GET"])
def test():
    return test_view_main(app)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    return signup_view_main(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    return login_view_main(app)


@app.errorhandler(404)
def page_not_found(error):
    # page not found時は何も言わず転送する
    return redirect(url_for("main"))


# ****** login必要（通常ユーザー） ******

@app.route("/")
@login_required
@log_info
def main():
    return main_view_main(app)


@app.route("/logout", methods=["GET", "POST"])
@login_required
@log_info
def logout():
    return logout_view_main(app)


@app.route("/book", methods=["GET", "POST"])
@login_required
@log_info
def book():
    return book_view_main(app)


@app.route("/borrow", methods=["POST"])
@login_required
@log_info
def borrow():
    return borrow_view_main(app)



# ****** login必要（管理者ユーザー） ******
def admin_required(func):
    @wraps(func)
    def admin_wrapper(*args, **keywords):
        # 管理者以外はbooksへ飛ばす
        if not current_user.is_admin:
            redirect(url_for("main"))
        return func(*args, **keywords)
    
    return admin_wrapper
    

@app.route("/maintenance", methods=["GET"])
@login_required
@admin_required
@log_info
def maintenance():
    return maintenance_view_main(app)


@app.route("/export_books", methods=["POST"])
@login_required
@admin_required
@log_info
def export_books():
    return export_books_view_main(app)


@app.route("/regist_book", methods=["POST"])
@login_required
@admin_required
@log_info
def regist_book():
    return regist_book_main(app)


@app.route("/get_book_with_isbn", methods=["POST"])
@login_required
@admin_required
@log_info
def get_book_with_isbn():
    return get_book_with_isbn_view_main(app)


@app.route("/member", methods=["GET", "POST"])
@login_required
@admin_required
@log_info
def member():
    return member_view_main(app)


@app.route("/regist_member_with_csv", methods=["POST"])
@login_required
@admin_required
@log_info
def regist_member_with_csv():
    return regist_member_with_csv_view_main(app)



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
