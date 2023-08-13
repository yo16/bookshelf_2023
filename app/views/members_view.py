from flask_login import current_user
from flask import render_template, url_for, redirect

from models import get_db, DbMember, DbBook
from .view_common import get_org_mem


def main(app, member_id=None):
    ret = None

    cur_member_id = member_id
    if cur_member_id is not None:
        # member_idが指定されている時は、指定されたmember_id
        cur_member_id = member_id

    else:
        # member_idがNoneの時は、自分
        cur_member_id = current_user.member_id

    # 表示
    ret = show_member_page(member_id, current_user.is_admin)
    if (ret is None):
        # 何かしらの不都合があったら、mainに飛ばす
        return redirect(url_for("main"))
    
    return ret


def show_member_page(member_id, is_admin=False):
    """各メンバーのページを表示

    Args:
        member_id (str): メンバーID
        is_admin (bool): カレントユーザーがadminかどうか

    Returns:
        str: 表示用のテンプレート
    """
    org_mem = get_org_mem()
    org_id = org_mem["organization"].org_id

    member = None
    hiss = []    
    with get_db() as db:
        # member
        member = DbMember.get(db, org_id, member_id)
        if (member is None):
            # 存在しないmember id
            return None
        # enabledでない場合は、adminのみが先に進める
        if (not member.is_enabled):
            if (not is_admin):
                return None

        # comment
        notes = DbBook.get_notes_by_member(db, org_id, member_id)

        # borrowed_his
        hiss = DbBook.get_bookhis_by_member(db, org_id, member_id)

    # 描画
    return render_template(
        "members.html",
        **org_mem,
        disp_member = member,
        notes = notes,
        histories = hiss
    )

