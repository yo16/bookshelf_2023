from flask_login import current_user
from flask import render_template
from sqlalchemy import select

from models import get_db, DbOrganization


def main(app):
    db = next(get_db())
    organization = db.execute(
        select(DbOrganization).where(DbOrganization.org_id == current_user.org_id)
    ).scalars().first()

    return render_template("maintenance.html", organization=organization, member=current_user)

