from flask import render_template, request
from flask_login import current_user
from sqlalchemy import select
from datetime import datetime

from models import get_db, DbBook, DbAuthor, DbWriting, DbPublisher, DbCollection, DbGenre, DbClassification
from .view_common import get_org_mem
from .forms import RegistBookForm


def main(app):
    form = RegistBookForm(request.form)
    org_mem = get_org_mem()

    if form.validate_on_submit():
        # 登録処理
        regist_info()
    
    # ジャンル一覧を取得
    genres = DbGenre.get_genres(org_mem["organization"].org_id)

    return render_template(
        "maintenance.html", **org_mem,
        form = form,
        genres = genres,
        now = datetime.now()
    )


def regist_info():
    """登録情報をもとに、関連テーブルを登録する
    """
    req = {
        "isbn": request.form["isbn"],
        "book_name": request.form["book_name"],
        "image_url": request.form["image_url"],
        "authors": [],
        "num_of_authors": int(request.form["num_of_authors"]),
        "publisher_code": request.form["publisher_code"],
        "publisher_name": request.form["publisher_name"],
        "comment": request.form["comment"],
        "genres": request.form["genres"],
        "org_id": int(request.form["org_id"]),
        "num_of_same_books": int(request.form["num_of_same_books"]),
        "added_dt": datetime.strptime(request.form["added_dt"], "%Y-%m-%d")
    }
    for i in range(req["num_of_authors"]):
        author = ""
        if f"author{i}" in request.form:
            author = request.form[f"author{i}"]
        req["authors"].append(author)
    
    # 登録する情報
    book, is_new_book = create_book(req)
    authors = None
    writings = None
    publisher = None
    classifications = None
    if is_new_book:
        authors = create_authors(req)
        writings = create_writings(req, book, authors)
        publisher = create_publisher(req)
        book.publisher_id = publisher.publisher_id
    classifications = create_classifications(req, book)
    collection, is_new_collection = create_collection(req, book)

    # 登録
    with get_db() as db:
        # 他のorg_idが登録済のbookの場合があり、
        # 完全に未登録の場合のみ、bookやauthors等を登録する
        if is_new_book:
            db.add(book)

            # 本が登録済の場合は、著者、writings、classificationも登録されているはず
            for a in authors:
                if a["is_new_author"]:
                    db.add(a["author"])
            for w in writings:
                db.add(w)
            db.add(publisher)
        
        for c in classifications:
            db.add(c)

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
            db.refresh(publisher)
            for c in classifications:
                db.refresh(c)
    
    return
    


def create_book(info):
    """登録するDbBookを作成

    Args:
        info (dict): requestから集めた情報
    Returns
        DbBook, Boolean
    """
    is_new_book = False
    # DBから本情報を取得
    cur_book = DbBook.get_book_by_isbn(info["isbn"])

    if cur_book is None:
        # なかったので、新しいIDを取得して作る
        is_new_book = True
        new_book_id = DbBook.get_new_book_id()
        cur_book = DbBook(
            book_id = new_book_id,
            isbn = info["isbn"],
            book_name = info["book_name"],
            image_url = info["image_url"],
            publisher_id = None
        )

    return cur_book, is_new_book


def create_authors(info):
    """登録するDbAuthorを作成

    Args:
        info (dict): requestから集めた情報
    """
    ret = []
    new_author_id = None
    new_author_count = -1

    for i, a in enumerate(info["authors"]):
        is_new_author = False

        # 登録済のDbAuthorがないか確認（名前で！）
        with get_db() as db:
            author = db.execute(
                select(DbAuthor).where(DbAuthor.author_name == a)
            ).scalar()
        if author is None:
            # 未登録なので登録
            is_new_author = True
            if not new_author_id:
                new_author_id = DbAuthor.get_new_author_id()
            new_author_count += 1
            author = DbAuthor(
                author_id = new_author_id + new_author_count,
                author_name = a
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


def create_publisher(info):
    """登録するDbPublisherを作成

    Args:
        info (dict): requestから集めた情報
    """
    new_pub_id = DbPublisher.get_new_publisher_id()
    publisher_code = DbPublisher.get_publisher_code_from_isbn(info["isbn"])
    publisher_name = f"code[{publisher_code}]"


    return DbPublisher(
        publisher_id = new_pub_id,
        publisher_name = publisher_name,
        publisher_code = publisher_code
    )


def create_collection(info, book):
    """Collectionを作成

    Args:
        info (dict): requestから集めた情報
        book (DbBook): 所有する本
    """
    is_new_collection = False
    # 登録済みかどうか確認
    collections = DbCollection.get_collection(
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
            num_of_same_books = info["num_of_same_books"],
            added_dt = info["added_dt"]
        )
    else:
        cur_collection = collections[0]

    return cur_collection, is_new_collection


def create_classifications(info, book):
    """classicifation（複数）を作成する

    Args:
        info (dict): requestから集めた情報
        book (DbBook): 所有する本
    """
    genres_str = info["genres"]

    # 指定がない場合は、分類なしの0が設定されたとみなす
    print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
    print(f">{genres_str}<")
    if (len(genres_str) == 0):
        print("LEN=0")
        genres_str = "0"
    
    genre_id_ary = genres_str.split(",")
    print(genre_id_ary)

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
