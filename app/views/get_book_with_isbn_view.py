from flask_login import current_user
from flask import jsonify, request
from sqlalchemy import select
import json
import requests
import urllib
from datetime import datetime
import re

from .view_common import get_org_mem
from models import DbBook, DbWriting, DbAuthor, DbPublisher, get_db

def main(app):
    """自分のDBを見に行って、なかったらGoogleAPIで検索する
    """
    org_mem = get_org_mem()
    isbn = request.json["isbn"]

    ret_dic = {"isbn": isbn}

    #print(10)
    # 組織と無関係にbook情報があるか確認
    cur_book = None
    with get_db() as db:
        cur_book = DbBook.get_book_by_isbn(db, isbn)

    #print(20)
    if cur_book:
        #print(100)
        with get_db() as db:
            # DBに見つかったので正式にbookと周辺情報を取得
            book_info = DbBook.get_book_info(
                db,
                cur_book.book_id,
                org_mem["organization"].org_id
            )

        ret_dic["book_name"] = cur_book.book_name
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
        ret_dic["authors"] = []
        for author in book_info["authors"]:
            ret_dic["authors"].append({
                "author_id": author.author_id,
                "author_name": author.author_name
            })
        
        # 出版者
        ret_dic["publisher_name"] = book_info["publisher"].publisher_name
        ret_dic["publisher_code"] = book_info["publisher"].publisher_code

        # collection
        if book_info["collection"]:
            ret_dic["num_of_same_books"] = book_info["collection"].num_of_same_books;
            ret_dic["added_dt"] = book_info["collection"].added_dt.strftime("%Y-%m-%d")
        else:
            # このケースはないはずだが一応・・・
            ret_dic["num_of_same_books"] = 0
            now_dt = datetime.now()
            ret_dic["added_dt"] = now_dt.strftime("%Y-%m-%d")
        
        # ジャンル
        ret_dic["genres"] = []
        if book_info["genres"]:
            for genre in book_info["genres"]:
                ret_dic["genres"].append({
                    "genre_id": genre.genre_id,
                    "genre_name": genre.genre_name
                })

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
        #print(volume_info)
        
        # volume_infoを得ることができたので、順に設定していく
        ret_dic["book_name"] = volume_info.get("title","")
        if "imageLinks" in volume_info:
            if "thumbnail" in volume_info["imageLinks"]:
                thumbnail = volume_info["imageLinks"]["thumbnail"]
                ret_dic["image_url"] = "https" + thumbnail[len("http"):]
        if "publishedDate" in volume_info:
            # APIで得る文字列のまま、設定する
            # (最後にjsonifyするため)
            pub_dt_str = volume_info["publishedDate"]
            # %dが入っていない時があるので、"-"が1つしかない場合は"-01"をつける
            if re.match(r"\d+-\d+$", pub_dt_str):
                pub_dt_str += "-01"
            ret_dic["published_dt"] = pub_dt_str
        else:
            ret_dic["published_dt"] = None
        ret_dic["original_description"] = volume_info.get("description", None)
        ret_dic["description"] = volume_info.get("description", None)
        ret_dic["page_count"] = volume_info.get("pageCount", None)
        if "dimensions" in volume_info:
            ret_dic["dimensions_height"] = volume_info["dimensions"].get("height", None)
            ret_dic["dimensions_width"] = volume_info["dimensions"].get("width", None)
            ret_dic["dimensions_thickness"] = volume_info["dimensions"].get("thickness", None)
        else:
            ret_dic["dimensions_height"] = None
            ret_dic["dimensions_width"] = None
            ret_dic["dimensions_thickness"] = None

        # 著者
        ret_dic["authors"] = []
        if "authors" in volume_info:
            for a in volume_info["authors"]:
                ret_dic["authors"].append({
                    "author_id": "",
                    "author_name": a
                })
        
        # 出版者
        ret_dic["publisher_code"] = DbPublisher.get_publisher_code_from_isbn(isbn)
        ret_dic["publisher_name"] = "to be implemented!"

        # collection
        now_dt = datetime.now()
        ret_dic["added_dt"] = now_dt.strftime("%Y-%m-%d")
        ret_dic["num_of_same_books"] = 0
        
        # ジャンル
        ret_dic["genres"] = []
    
    # 構築において、すべての項目を設定しているはずであることの確認
    # 項目の追加をした時には、必ず追加すること
    assert "isbn" in ret_dic
    assert "book_name" in ret_dic
    assert "image_url" in ret_dic
    assert "published_dt" in ret_dic
    assert "page_count" in ret_dic
    assert "dimensions_height" in ret_dic
    assert "dimensions_width" in ret_dic
    assert "dimensions_thickness" in ret_dic
    assert "original_description" in ret_dic
    assert "description" in ret_dic
    assert "authors" in ret_dic
    assert "publisher_name" in ret_dic
    assert "publisher_code" in ret_dic
    assert "num_of_same_books" in ret_dic
    assert "added_dt" in ret_dic
    assert "genres" in ret_dic

    #print(1000)
    return jsonify(ResultSet=json.dumps(ret_dic))
