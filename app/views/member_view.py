from flask_login import current_user
from flask import render_template, request

from models import DbMember
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
            print("regist!!!!!!!!!!")

        elif (method=="PUT"):
            # 編集
            print("edit!!!!!!!!!!")

        elif (method=="DELETE"):
            # 削除
            print("delete!!!!!!!!!!")

    # 組織内のメンバーを取得
    members = DbMember.get_members_in_org(org_mem["organization"].org_id)

    return render_template(
        "member.html", **org_mem,
        regist_form = regist_form,
        edit_form = edit_form,
        delete_form = delete_form,
        members = members
    )
