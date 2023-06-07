from flask_login import current_user
from flask import render_template, request
from sqlalchemy import update, delete
from sqlalchemy.sql.expression import and_

from models import get_db, DbMember
from .view_common import get_org_mem
from .forms import RegistMemberForm, EditMemberForm, DeleteMemberForm


def main(app):
    org_mem = get_org_mem()
    regist_form = RegistMemberForm(request.form)
    regist_form.method.data = "POST"
    edit_form = EditMemberForm(request.form)
    edit_form.method.data = "PUT"
    delete_form = DeleteMemberForm(request.form)
    delete_form.method.data = "DELETE"

    # 本来は、methodを分けたいが、ブラウザが対応していないので
    # formの中身で分岐する
    if regist_form.is_submitted():
        method = request.form.get("method")
        if (method=="POST"):
            # 追加
            regist_member(
                org_mem["organization"],
                request.form
            )

        elif (method=="PUT"):
            # 編集
            edit_member(
                org_mem["organization"],
                request.form
            )

        elif (method=="DELETE"):
            # 削除
            delete_member(
                org_mem["organization"],
                request.form
            )

    # 組織内のメンバーを取得
    members = DbMember.get_members_in_org(org_mem["organization"].org_id)

    return render_template(
        "members.html", **org_mem,
        regist_form = regist_form,
        edit_form = edit_form,
        delete_form = delete_form,
        members = members
    )


def regist_member(organization, form):
    """登録

    Args:
        organization (DbOrganization): 組織情報
        form (request.form): 登録情報
    """
    with get_db() as db:
        # 次のID
        next_member_id = DbMember.get_new_member_id(organization.org_id)

        # パスワードをハッシュ化
        hashed_pass = DbMember.hash_password(form.get("reg_password"))

        mem = DbMember(
            org_id = organization.org_id,
            member_id = next_member_id,
            password_hashed = hashed_pass,
            member_name = form.get("reg_member_name"),
            member_code = form.get("reg_member_code"),
            is_admin = True if form.get("reg_is_admin")=="1" else False,
            is_enabled = True
        )
        db.add(mem)
        db.commit()
        db.refresh(mem)


def edit_member(organization, form):
    """編集

    Args:
        organization (DbOrganization): 組織情報
        form (request.form): 編集情報
    """
    with get_db() as db:
        editform_password = form.get("edit_password")
        
        if (len(editform_password) > 0):
            # パスワードがある（変更する）場合
            # パスワードをハッシュ化
            hashed_pass = DbMember.hash_password(editform_password)

            stmt = update(
                DbMember
            ).values(
                member_name = form.get("edit_member_name"),
                member_code = form.get("edit_member_code"),
                password_hashed = hashed_pass,
                is_admin = True if (form.get("edit_is_admin")=="1") else False,
                is_enabled = True if (form.get("edit_is_enabled")=="1") else False
            ).where(
                and_(
                    DbMember.org_id == organization.org_id,
                    DbMember.member_id == int(form.get("edit_member_id"))
                )
            )
        else:
            # パスワードがない（変更しない）場合
            stmt = update(
                DbMember
            ).values(
                member_name = form.get("edit_member_name"),
                member_code = form.get("edit_member_code"),
                is_admin = True if (form.get("edit_is_admin")=="1") else False,
                is_enabled = True if (form.get("edit_is_enabled")=="1") else False
            ).where(
                and_(
                    DbMember.org_id == organization.org_id,
                    DbMember.member_id == int(form.get("edit_member_id"))
                )
            )

        db.execute(stmt)
        db.commit()


def delete_member(organization, form):
    """削除

    Args:
        organization (DbOrganization): 組織情報
        form (request.form): 削除情報
    """
    with get_db() as db:
        stmt = delete(
            DbMember
        ).where(
            and_(
                DbMember.org_id == organization.org_id,
                DbMember.member_id == int(form.get("del_member_id"))
            )
        )
        db.execute(stmt)
        db.commit()
