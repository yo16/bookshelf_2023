from flask_login import logout_user
from flask import redirect, url_for, request
from sqlalchemy import select

from models import get_db, DbOrganization
from views.view_common import get_org_mem
from views.forms import LoginForm

def main(app):
    logout_user()

    form = LoginForm(request.form)
    message = "ログアウトしました"
    return redirect(url_for("login", message=message))
