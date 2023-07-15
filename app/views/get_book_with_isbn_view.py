from flask_login import current_user
from flask import jsonify, request
from sqlalchemy import select
import json
import requests
import urllib

from models import get_db, DbBook, DbWriting, DbAuthor, DbPublisher

def main(app):
    """自分のDBを見に行って、なかったらGoogleAPIで検索する
    """
    isbn = request.json["isbn"]

    ret_dic = {
        "isbn": isbn,
        "book_name": "",
        "authors": [],
        "publisher": "",
        "publisher_code": "",
        "image_url": "",
        "comment": "",
        "genres": ""
    }

    #print(10)
    # DBを探す
    with get_db() as db:
        cur_book = db.execute(
            select(DbBook).where(DbBook.isbn == isbn)
        ).scalars().first()

        #print(20)
        if cur_book:
            #print(100)
            # DBに見つかったので関連情報を取得
            ret_dic["book_name"] = cur_book.book_name
            ret_dic["publisher_id"] = cur_book.publisher_id
            ret_dic["image_url"] = cur_book.image_url

            # 著者
            writings = db.execute(
                select(DbWriting).where(DbWriting.book_id == cur_book.book_id)
            ).scalars().all()
            for cur_writing in writings:
                author = db.execute(
                    select(DbAuthor).where(DbAuthor.author_id == cur_writing.author_id)
                ).scalars().first()
                ret_dic["authors"].append({
                    "author_id": author.author_id,
                    "author_name": author.author_name
                })
            
            # 出版社
            publisher = db.execute(
                select(DbPublisher).where(DbPublisher.publisher_id == cur_book.publisher_id)
            ).scalars().first()
            ret_dic["publisher_name"] = publisher.publisher_name
            ret_dic["publisher_code"] = publisher.publisher_code

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
            ret_dic["book_name"] = item["volumeInfo"]["title"]
            if "authors" in item["volumeInfo"]:
                for a in item["volumeInfo"]["authors"]:
                    ret_dic["authors"].append({
                        "author_id": "",
                        "author_name": a
                    })
            if "imageLinks" in item["volumeInfo"]:
                if "thumbnail" in item["volumeInfo"]["imageLinks"]:
                    thumbnail = item["volumeInfo"]["imageLinks"]["thumbnail"]
                    ret_dic["image_url"] = "https" + thumbnail[len("http"):]
            
            ret_dic["publisher_code"] = DbPublisher.get_publisher_code_from_isbn(isbn)
            ret_dic["publisher_name"] = "to be implemented!"

            #print("999")
            #print(ret_dic)

    
    # ジャンル

    #print(1000)
    return jsonify(ResultSet=json.dumps(ret_dic))
