import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session

# SQLAlchemy based on
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
# https://fastapi.tiangolo.com/ja/tutorial/sql-databases/#create-the-database-models

# engine
engine = None

# sessionmaker
SessionLocal = None


# Base
class Base(DeclarativeBase):
    pass


def create_sqlalchemy_engine(app):
    """接続engineを設定する
    """
    global engine
    global SessionLocal
    
    host = app.config["DBHOST"]
    db = app.config["DBNAME"]
    user = app.config["DBUSER"]
    passwd = app.config["DBPASS"]
    charset = app.config["DBCHARSET"]
    port = 3306

    debug = app.config["DEBUG"]

    connect_str = f"mysql+mysqlconnector://{user}:{passwd}@{host}:{port}/{db}?charset={charset}"
    engine = create_engine(url=connect_str, echo=debug)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    """セッションを作成する, commitは呼び出し側で行うこと
    """
    global SessionLocal
    
    db = SessionLocal()
    """
    try:
        yield db
    finally:
        db.close()
    """
    return db
