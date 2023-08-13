from flask import render_template

from models import get_db, DbMember
from .view_common import get_org_mem


def main(app):
    ret = show_admin_members_page()
    
    return ret


def show_admin_members_page():
    """admin用のメンバー管理ページを表示
    またそこから投げられたPOSTの対応もする

    Returns:
        str: 表示用のテンプレート
    """
    org_mem = get_org_mem()

    members = []
    # DB接続しなおして、情報を取得
    # (再接続は冗長だとは思うが、登録と取得で処理を明確に分ける意識)
    with get_db() as db:
        # 組織内のメンバーを取得
        members = DbMember.get_members_in_org(db, org_mem["organization"].org_id)

    return render_template(
        "members_all.html", **org_mem,
        members = members
    )

