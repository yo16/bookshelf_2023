from flask import render_template, request
from flask_login import current_user
from sqlalchemy import select

from models import get_db, DbOrganization
from views.view_common import get_org_mem
from views.forms import RegistBookForm


def main(app):
    form = RegistBookForm(request.form)

    org_mem = get_org_mem()
    return render_template("maintenance.html", **org_mem, form=form)
