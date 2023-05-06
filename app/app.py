# coding:utf-8
from flask import Flask, request, abort
import logging
import json
import mysql.connector

from app_logger import initialize_logger

# アプリケーション
app = Flask(__name__)
app.config.from_file("development.json", load=json.load, silent=True)

# ロガーを設定
initialize_logger(app.logger)

# DB



# ------ api ------

@app.route("/")
def hello_world():
    app.logger.info("hello world!")
    return "hello world!"

@app.route("/test", methods=["GET"])
def test():
    con = getDbConnection()
    cur = con.cursor()
    cur.execute("select count(*) from organization;")
    text = ""
    for cnt in cur:
        text += f"{cnt},"
    cur.close()
    con.close()
    
    return "test ok!<br />" + text, 404


def getDbConnection():
    return mysql.connector.connect(
        host=app.config["DBHOST"],
        db=app.config["DBNAME"],
        user=app.config["DBUSER"],
        passwd=app.config["DBPASS"],
        charset=app.config["DBCHARSET"]
    )


if __name__=='__main__':
    app.run(host='0.0.0.0')
