from flask_login import current_user
from flask import render_template, redirect, url_for, request
from sqlalchemy import select

from models import get_db, DbOrganization, DbMember, DbGenre
from views.view_common import get_org_mem
from views.login_form import LoginForm


def main(app):
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
