from flask import render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import select
from datetime import datetime
import re

from models import get_db, DbBook, DbAuthor, DbWriting, DbPublisher, DbCollection, DbGenre, DbClassification
from .view_common import get_org_mem, get_image_file_path
from .forms import RegistBookForm


def main(app):
    form = RegistBookForm(request.form)
    org_mem = get_org_mem()

    book_info = None
    genres = []
    with get_db() as db:
        # getでbook_idが指定されている場合は、DBから情報を取得
        book_id = request.args.get("book_id", None)
        if book_id:
            book_info = DbBook.get_book_info(db, book_id, org_mem["organization"].org_id)
            form.isbn.data = book_info["book"].isbn

        # postでsubmitされている場合は、登録
        if form.validate_on_submit():
            # 登録処理（内部でcommitする）
            new_book_id = regist_info(app, db, org_mem["organization"].org_id)

            # 登録が終わったら、登録済みのmaintenanceページを表示
            return redirect(url_for("maintenance", book_id=new_book_id))

        # ジャンル一覧を取得
        genres = DbGenre.get_genres(db, org_mem["organization"].org_id)
    
    # ジャンル名に階層を示すスペーサーを埋め込む
    for g in genres:
        # 階層
        floor_num = len(g.sort_key.split("_")) - 1
        # 字下げ
        floor_spacer = "　" * (floor_num - 1)
        # スペーサーを入れる
        g.genre_name = floor_spacer + g.genre_name

    return render_template(
        "maintenance.html", **org_mem,
        form = form,
        book_info = book_info,
        genres = genres,
        now = datetime.now()
    )


def regist_info(app, db, org_id):
    """登録情報をもとに、関連テーブルを登録する（この関数内部でcommitする）
    """
    req = {
        "isbn": request.form["isbn"],
        "book_name": request.form["book_name"],
        "image_url": request.form["image_url"],
        "authors": [ a for a in request.form["authors"].split("\n") if len(a)>0 ],
        "publisher_code": request.form["publisher_code"],
        "publisher_name": request.form["publisher_name"],
        "published_dt": None,
        "original_description": request.form["original_description"],
        "description": request.form["description"],
        "page_count": None,
        "dimensions_height": None,
        "dimensions_width": None,
        "dimensions_thickness": None,
        "genres": request.form["genres"],
        "org_id": org_id,
        "num_of_same_books": int(request.form["num_of_same_books"]),
        "added_dt": datetime.strptime(request.form["added_dt"], "%Y-%m-%d")
    }
    # published_dt
    try:
        dt_str = request.form["published_dt"]
        # %dが入っていない時があるので、"-"が1つしかない場合は"-01"をつける
        if re.match(r"\d+-\d+$", dt_str):
            dt_str += "-01"
        req["published_dt"] = datetime.strptime(dt_str, "%Y-%m-%d")
    except:
        req["published_dt"] = None
    # 任意項目でintのもの
    optional_int_items = ["page_count", "dimensions_height", "dimensions_width", "dimensions_thickness"]
    for item in optional_int_items:
        # 空や数値でない場合はNone(NULL)とする
        try:
            req[item] = int(request.form[item])
        except Exception as e:
            req[item] = None
    
    # 登録する情報
    book, is_new_book = create_book(app, db, req)
    authors = None
    writings = None
    publisher = None
    is_new_pub = False
    classifications = None
    if is_new_book:
        authors = create_authors(db, req)
        writings = create_writings(req, book, authors)
        publisher, is_new_pub = create_publisher(db, req)
        book.publisher_id = publisher.publisher_id
    classifications = create_classifications(req, book)
    collection, is_new_collection = create_collection(db, req, book)

    # 登録
    # 他のorg_idが登録済のbookの場合があり、
    # 完全に未登録の場合のみ、bookやauthors等を登録する
    if is_new_book:
        # book
        db.add(book)

        # author
        for a in authors:
            if a["is_new_author"]:
                db.add(a["author"])
        
        # writing
        for w in writings:
            db.add(w)

        # publisher
        if is_new_pub:
            db.add(publisher)
    
    # classification
    edit_classifications = []
    if is_new_book:
        # 新規の場合は、単純にclassificationsを追加
        for c in classifications:
            db.add(c)
            edit_classifications.append(c)
    else:
        # 既存のbookの場合は、追加分を追加し、削除されたものは削除、それ以外は何もしない
        exists_classes = DbClassification.get_classifications(db, org_id, book.book_id)
        for c_e in exists_classes:  # すでにあるもの
            exists_in_newer_list = False
            for c_a in classifications: # これから追加しようとしているもの
                if (c_e.org_id==c_a.org_id) and (c_e.book_id==c_a.book_id) and (c_e.genre_id==c_a.genre_id):
                    # あった
                    exists_in_newer_list = True
            if not exists_in_newer_list:
                # 新しいリストになかったら、既存は削除
                db.delete(c_e)
        for c_a in classifications: # これから追加しようとしているもの
            exists_in_older_list = False
            for c_e in exists_classes:  # すでにあるもの
                if (c_e.org_id==c_a.org_id) and (c_e.book_id==c_a.book_id) and (c_e.genre_id==c_a.genre_id):
                    # あった
                    exists_in_older_list = True
            if not exists_in_older_list:
                # 既存のリストになかったら、追加
                db.add(c_a)
                edit_classifications.append(c_a)

    # collection
    if is_new_collection:
        db.add(collection)
    
    db.commit()

    # 片付け
    if is_new_book:
        db.refresh(book)

        for a in authors:
            if a["is_new_author"]:
                db.refresh(a["author"])
        for w in writings:
            db.refresh(w)
        if is_new_pub:
            db.refresh(publisher)
    for c in edit_classifications:
        db.refresh(c)
    db.refresh(collection)
    
    return book.book_id
    


def create_book(app, db, info):
    """登録するDbBookを作成

    Args:
        app
        db
        info (dict): requestから集めた情報
    Returns
        DbBook, Boolean
    """
    is_new_book = False
    # DBから本情報を取得
    cur_book = DbBook.get_book_by_isbn(db, info["isbn"])

    if cur_book is None:
        # なかったので、新しいIDを取得して作る
        is_new_book = True
        new_book_id = DbBook.get_new_book_id(db)

        # 画像のurlから画像をダウンロードして、そのパスを取得しておく
        image_local_path = get_image_file_path(app, new_book_id, info["image_url"])
        
        # 本情報を作成
        cur_book = DbBook(
            book_id = new_book_id,
            isbn = info["isbn"],
            book_name = info["book_name"],
            image_url = info["image_url"],
            publisher_id = None,
            published_dt = info["published_dt"],
            page_count = info["page_count"],
            dimensions_height = info["dimensions_height"],
            dimensions_width = info["dimensions_width"],
            dimensions_thickness = info["dimensions_thickness"],
            original_description = info["original_description"],
            image_local_path = image_local_path,
        )

    return cur_book, is_new_book


def create_authors(db, info):
    """登録するDbAuthorを作成

    Args:
        info (dict): requestから集めた情報
    """
    ret = []
    new_author_id = None
    new_author_count = -1

    for i, a in enumerate(info["authors"]):
        is_new_author = False
        
        # 著者名
        author_name = re.sub(r"[\r\n]", "", a)

        # 登録済のDbAuthorがないか確認（名前で！）
        author = db.execute(
            select(DbAuthor).where(DbAuthor.author_name == author_name)
        ).scalar()
        if author is None:
            # 未登録なので登録
            is_new_author = True
            if not new_author_id:
                new_author_id = DbAuthor.get_new_author_id(db)
            new_author_count += 1
            author = DbAuthor(
                author_id = new_author_id + new_author_count,
                author_name = author_name
            )
        else:
            # 登録されている
            is_new_author = False
            author = author
        
        # 登録する/しないによらずappend
        ret.append({
            "author": author,
            "is_new_author": is_new_author
        })
    
    return ret


def create_writings(info, book, authors):
    """登録するDbWritingを作成

    Args:
        info (dict): requestから集めた情報
        book (DbBook): 登録する本情報
        authors (array[DbAuthor]): 登録する著者情報の配列
    Returns:
        array[DbWriting]
    """
    ret = []

    for a in authors:
        ret.append(DbWriting(
            book_id = book.book_id,
            author_id = a["author"].author_id
        ))
    
    return ret


def create_publisher(db, info):
    """登録するDbPublisherを作成

    Args:
        info (dict): requestから集めた情報
    Returns:
        DbPubliser: isbnから検索または作成したpublisher
        bool: True:新規作成, False:検索(既存)
    """
    # publisher_codeが指定されている場合は、すでに存在していないか確認し
    # 存在している場合は作成しない
    publisher_code = DbPublisher.get_publisher_code_from_isbn(info["isbn"])
    if (len(info["isbn"]) > 0):
        registed_pub = DbPublisher.get_publisher_by_pubcode(db, publisher_code)
        if registed_pub:
            return registed_pub, False

    new_pub_id = DbPublisher.get_new_publisher_id(db)
    publisher_name = f"code[{publisher_code}]"

    return DbPublisher(
        publisher_id = new_pub_id,
        publisher_name = publisher_name,
        publisher_code = publisher_code
    ), True


def create_collection(db, info, book):
    """Collectionを作成

    Args:
        info (dict): requestから集めた情報
        book (DbBook): 所有する本
    """
    is_new_collection = False
    # 登録済みかどうか確認
    collections = DbCollection.get_collection(
        db,
        org_id = info["org_id"],
        book_id = book.book_id
    )

    cur_collection = None
    if (collections is None) or (len(collections) == 0):
        # なかったので、作る
        is_new_collection = True
        cur_collection = DbCollection(
            org_id = info["org_id"],
            book_id = book.book_id,
            num_of_same_books = int(info["num_of_same_books"]),
            description = info["description"],
            added_dt = info["added_dt"]
        )
    else:
        # 既存の場合は、infoの情報をもとに更新する
        cur_collection = collections[0]
        cur_collection.num_of_same_books = int(info["num_of_same_books"])
        cur_collection.description = info["description"]

    return cur_collection, is_new_collection


def create_classifications(info, book):
    """classicifation（複数）を作成する

    Args:
        info (dict): requestから集めた情報
        book (DbBook): 所有する本
    """
    genres_str = info["genres"]

    # 指定がない場合は、分類なしの0が設定されたとみなす
    if (len(genres_str) == 0):
        print("LEN=0")
        genres_str = "0"
    
    # カンマ区切りで数字を取り出す
    genre_id_ary = [ int(s) for s in genres_str.split(",") if len(s)>0 ]

    ret_genres = []
    for g_id in genre_id_ary:
        ret_genres.append(
            DbClassification(
                org_id = info["org_id"],
                genre_id = g_id,
                book_id = book.book_id
            )
        )
    
    return ret_genres
