# coding:utf-8
from flask import Flask, request, abort
import logging
import json

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
    return "test ok!", 404


if __name__=='__main__':
    app.run(host='0.0.0.0')
