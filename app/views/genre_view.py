from flask import render_template, request
from sqlalchemy import select

from models import get_db, DbGenre
from .view_common import get_org_mem
from .forms import RegistGenreForm


def main(app):
    form = RegistGenreForm(request.form)
    org_mem = get_org_mem()

    genres = get_genre_info(org_mem["organization"].org_id)
    
    return render_template(
        "genre.html",
        **org_mem,
        form = form,
        genres = genres
    )


def get_genre_info(org_id):
    genres = DbGenre.get_genres(org_id)
    p_genres = DbGenre.pretty_genres(genres)
    return p_genres

