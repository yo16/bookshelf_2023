from flask import render_template, redirect, url_for, request
from flask_login import login_user

from views.forms import LoginForm
from models import DbMember


def main(app):
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
            return redirect(url_for("main"))
        
        # 認証失敗
        message = "組織ID、ユーザー名、またはパスワードが正しくありません。"
        return render_template("login.html", message=message, form=form)
    
    # 初期値
    message = request.args.get('message')
    form.org_id.data = request.args.get('org_id')
    form.member_code.data = request.args.get('member_code')
    return render_template("login.html", form=form, message=message)
