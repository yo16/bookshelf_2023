from flask import url_for
from flask_login import current_user
import os
import urllib
import hashlib

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


#def get_image_path(app, book_id, image_url):
    """ローカルにbook_idの画像がある場合はそのままパスを返す
    存在しない場合は、image_urlからダウンロードして、パスを返す

    Args:
        book_id (int): 本ID
    
    Returns:
        (str): ローカルファイルパス
    """
#     # ダウンロード先のローカルファイルパス
#     image_file_path = get_image_file_path(app, book_id)
# 
#     return_str = image_url
#     if not os.path.isfile(image_file_path):
#         # 存在しなかったらダウンロードする
#         try:
#             print("--------------------------------")
#             print(image_url)
#             with urllib.request.urlopen(image_url) as web_file:
#                 data = web_file.read()
#                 with open(image_file_path, mode='wb') as local_file:
#                     local_file.write(data)
# 
#             # return_strを書き換える
#             return_str = url_for("static", filename=f"img/book/{book_id}")
# 
#         except urllib.error.URLError as e:
#             # エラーが起きたら何もしない（URLから取得し続ける）
#             pass
#     else:
#         # 存在している場合は、jinja2でローカルを取得するようurlを返す
#         # return_strを書き換える
#         return_str = url_for("static", filename=f"img/book/{book_id}")
# 
#     return return_str


def get_image_file_path(app, book_id, image_url, filename_length=20):
    """画像ファイルのパスを決める
    book_idから適当にハッシュ化した文字列から、
    それが存在していたらもう一度ハッシュ化して
    存在しなくなるまで繰り返した文字列を、ファイル名とする。
    （戻せないが、問題ない認識）

    Args:
        app: app
        book_id (int): book id
        image_url (str): Googleから取得した画像のURL
        filename_length (int): ローカルに保存する画像のファイル名の長さ
    """
    # ローカルに保存するフォルダ
    image_dir = app.config["IMAGE_DIR"]
    # ローカルに保存するファイル名、パス
    image_file_name = None
    image_file_path = None

    # 前ゼロして、初期のファイル名とする
    cur_file_name = f"{book_id}".zfill(filename_length)

    hasher = hashlib.sha3_512()
    file_is_exists = True
    hashed_cur_file_name = None
    while file_is_exists:
        # ファイル名をハッシュ化
        hasher.update(cur_file_name.encode("utf-8"))

        # filename_lengthで切っちゃう
        hashed_cur_file_name = hasher.hexdigest()[:filename_length]

        # ファイルパスを仮決め
        cur_file_path = f"{image_dir}/{hashed_cur_file_name}"

        # 存在しているか確認
        if not os.path.exists(cur_file_path):
            # 存在していなければこの名前で決定
            image_file_name = hashed_cur_file_name
            file_is_exists = False
        else:
            # 存在していたら、もう一度トライ
            cur_file_name = hashed_cur_file_name
    
    # ファイル名、ファイルパスが決定
    image_file_path = f"{image_dir}/{image_file_name}"
    
    # ファイルをダウンロードする
    try:
        with urllib.request.urlopen(image_url) as web_file:
            data = web_file.read()
            with open(image_file_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        # エラーが起きたら何もしない（URLから取得し続ける）
        return None

    # 決まったファイル名を、ブラウザから見られるように適当に変える
    browser_url = url_for("static", filename=f"img/book/{image_file_name}")

    return browser_url

