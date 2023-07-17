from flask_login import current_user
from flask import jsonify, request
from sqlalchemy import select
import json
import requests
import urllib
from datetime import datetime

from .view_common import get_org_mem
from models import DbBook, DbWriting, DbAuthor, DbPublisher

def main(app):
    """自分のDBを見に行って、なかったらGoogleAPIで検索する
    """
    org_mem = get_org_mem()
    isbn = request.json["isbn"]

    ret_dic = {
        "isbn": isbn,
        "book_name": "",
        "image_url": "",
        "published_dt": None,
        "description": None,
        "page_count": None,
        "dimensions_height": None,
        "dimensions_width": None,
        "dimensions_thickness": None,
        "authors": [],
        "publisher_name": "",
        "publisher_code": "",
    }

    #print(10)
    # 組織と無関係にbook情報があるか確認
    cur_book = DbBook.get_book_by_isbn(isbn)

    #print(20)
    if cur_book:
        #print(100)
        # DBに見つかったので正式にbookと周辺情報を取得
        book_info = DbBook.get_book_info(
            cur_book.book_id,
            org_mem["organization"].org_id
        )

        ret_dic["book_name"] = cur_book.book_name
        ret_dic["publisher_id"] = cur_book.publisher_id
        ret_dic["image_url"] = cur_book.image_url
        ret_dic["published_dt"] = cur_book.published_dt.strftime("%Y-%m-%d")
        ret_dic["page_count"] = cur_book.page_count
        ret_dic["dimensions_height"] = cur_book.dimensions_height
        ret_dic["dimensions_width"] = cur_book.dimensions_width
        ret_dic["dimensions_thickness"] = cur_book.dimensions_thickness
        ret_dic["original_description"] = cur_book.original_description
        if book_info["collection"]:
            ret_dic["description"] = book_info["collection"].description
        else:
            # まだ組織にない本の場合は、original_descriptionを設定する
            ret_dic["description"] = cur_book.original_description

        # 著者
        for author in book_info["authors"]:
            ret_dic["authors"].append({
                "author_id": author.author_id,
                "author_name": author.author_name
            })
        
        # 出版者
        ret_dic["publisher_name"] = book_info["publisher"].publisher_name
        ret_dic["publisher_code"] = book_info["publisher"].publisher_code

    else:
        #print(200)
        # 見つからなかったので、Googleに問い合わせる
        url = f"https://www.googleapis.com/books/v1/volumes"
        params = {
            "q": f"isbn:{isbn}",
            "country": "JP"
        }
        params_urlencoded = urllib.parse.urlencode(params)
        #params_urlencoded = params_urlencoded.encode("ascii")
        url_params = f"{url}?{params_urlencoded}"
        #print(f"210:{url_params}")
        
        #res = requests.get(url, params=params)
        res = requests.get(url_params)
        #print("211")
        #print(res)
        #print(res.text)
        res_data = json.loads(res.text)

        item = res_data["items"][0]
        volume_info = item["volumeInfo"]
        print(volume_info)
        
        # volume_infoを得ることができたので、順に設定していく
        ret_dic["book_name"] = volume_info.get("title","")
        if "imageLinks" in volume_info:
            if "thumbnail" in volume_info["imageLinks"]:
                thumbnail = volume_info["imageLinks"]["thumbnail"]
                ret_dic["image_url"] = "https" + thumbnail[len("http"):]
        if "publishedDate" in volume_info:
            # APIで得る文字列のまま、設定する
            # (最後にjsonifyするため)
            ret_dic["published_dt"] = volume_info["publishedDate"]
        else:
            ret_dic["published_dt"] = None
        ret_dic["description"] = volume_info.get("description", None)
        ret_dic["page_count"] = volume_info.get("pageCount", None)
        if "dimensions" in volume_info:
            ret_dic["dimensions_height"] = volume_info["dimensions"].get("height", None)
            ret_dic["dimensions_width"] = volume_info["dimensions"].get("width", None)
            ret_dic["dimensions_thickness"] = volume_info["dimensions"].get("thickness", None)

        # 著者
        if "authors" in volume_info:
            for a in volume_info["authors"]:
                ret_dic["authors"].append({
                    "author_id": "",
                    "author_name": a
                })
        
        # 出版者
        ret_dic["publisher_code"] = DbPublisher.get_publisher_code_from_isbn(isbn)
        ret_dic["publisher_name"] = "to be implemented!"

        #print("999")
        #print(ret_dic)

    
    # ジャンル

    #print(1000)
    return jsonify(ResultSet=json.dumps(ret_dic))
