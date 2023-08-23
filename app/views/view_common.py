from flask import url_for
from flask_login import current_user
import os
import urllib

from models import get_db, DbOrganization


def get_org_mem():
    """組織とメンバー情報を取得

    Returns:
        dict: {organization:DbOrganization, member:DbMember}
    """
    org = None
    with get_db() as db:
        org = DbOrganization.get(db, current_user.org_id)

    return {
        "organization": org,
        "member": current_user
    }


def get_image_path(app, book_id, image_url):
    """ローカルにbook_idの画像がある場合はそのままパスを返す
    存在しない場合は、image_urlからダウンロードして、パスを返す

    Args:
        book_id (int): 本ID
    
    Returns:
        (str): ローカルファイルパス
    """
    # あるとしたらのファイルパス
    image_dir = app.config["IMAGE_DIR"]
    image_file_path = f"{image_dir}/{book_id}"

    return_str = image_url
    if not os.path.isfile(image_file_path):
        # 存在しなかったらダウンロードする
        try:
            print("--------------------------------")
            print(image_url)
            with urllib.request.urlopen(image_url) as web_file:
                data = web_file.read()
                with open(image_file_path, mode='wb') as local_file:
                    local_file.write(data)

            # return_strを書き換える
            return_str = url_for("static", filename=f"img/book/{book_id}")

        except urllib.error.URLError as e:
            # エラーが起きたら何もしない（URLから取得し続ける）
            pass
    else:
        # 存在している場合は、jinja2でローカルを取得するようurlを返す
        # return_strを書き換える
        return_str = url_for("static", filename=f"img/book/{book_id}")

    return return_str
