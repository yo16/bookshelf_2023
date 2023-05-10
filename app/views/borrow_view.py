from flask import redirect, url_for


def main(app):
    return redirect(url_for("main"))

