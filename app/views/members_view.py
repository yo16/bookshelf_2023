from flask_login import current_user
from flask import render_template, request
from sqlalchemy import update, delete
from sqlalchemy.sql.expression import and_

from models import get_db, DbMember, DbBook
from .view_common import get_org_mem
from .forms import RegistMemberForm, EditMemberForm, DeleteMemberForm


def main(app, member_id):
    ret = None

    if member_id is not None:
        # member_idが指定されている時は、memberページを表示
        ret = show_member_page(app, member_id)
        
    else:
        org_mem = get_org_mem()
        if (not current_user.is_admin):
            # 管理者ではない場合、自分のページを表示する
            member_id = current_user.member_id
            ret = show_member_page(app, member_id)
            
        else:
            # adminの場合は、memberの管理ページ(members)を表示
            ret = show_members_page(app)
    
    return ret


def show_member_page(app, member_id):
    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id
    
    # member
    member = DbMember.get(org_id, member_id)

    # borrowed_his
    hiss = DbBook.get_bookhis_by_member(org_id, member_id)

    # 描画
    return render_template(
        "member.html",      # membersではなく、member固有のページ
        **org_mem,
        disp_member = member,
        histories = hiss
    )


def show_members_page(app):
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
