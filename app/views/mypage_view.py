from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbGenre
from .view_common import get_org_mem
#from .forms import RegistMypageForm
from .forms import RegistGenreForm



def main(app):
    #form = RegistMypageForm(request.form)
    form = RegistGenreForm(request.form)
    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id

    if form.validate_on_submit():
        # 登録
        pass

    # 登録されているgenre情報を取得
    #genres = get_mypage_info(org_id)

    # 描画
    return render_template(
        "mypage.html",
        **org_mem
    )

