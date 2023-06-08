from flask_login import logout_user, current_user
from flask import redirect, url_for, request
from .forms import LoginForm

def main(app):
    org_id = current_user.org_id
    logout_user()

    form = LoginForm(request.form)
    message = f"ログアウトしました.(org_id={org_id})"
    return redirect(url_for("login", message=message))
