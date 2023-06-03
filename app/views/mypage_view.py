from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbMember, DbBook
from .view_common import get_org_mem
#from .forms import RegistMypageForm
from .forms import RegistGenreForm



def main(app):
    #form = RegistMypageForm(request.form)
    form = RegistGenreForm(request.form)
    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id
    member_id = request.args.get("mem_id")

    # member_idがある場合はそのmember、ない場合はログインユーザー
    if ((member_id is None) or (len(member_id) == 0)):
        # 指定がないのでログインユーザー
        member_id = org_mem["member"].member_id

    if form.validate_on_submit():
        # 登録
        pass
    
    # member
    member = DbMember.get(org_id, member_id)

    # borrowed_his
    hiss = DbBook.get_bookhis_by_member(org_id, member_id)

    # 描画
    return render_template(
        "mypage.html",
        **org_mem,
        disp_member = member,
        histories = hiss
    )

