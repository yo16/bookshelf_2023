from flask import render_template

from .view_common import get_org_mem


def main(app):
    org_mem = get_org_mem()

    book_upper_limit = app.config["BOOK_UPPER_LIMIT"]
    
    return render_template(
        "billing.html",
        **org_mem,
        book_upper_limit = book_upper_limit,
    )
