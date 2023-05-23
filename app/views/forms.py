import flask_wtf
import wtforms

# ログインフォーム
class LoginForm(flask_wtf.FlaskForm):
    org_id = wtforms.IntegerField(
        'org_id',
        [wtforms.validators.InputRequired()]
    )
    member_code = wtforms.StringField(
        'member_code',
        [wtforms.validators.InputRequired()]
    )
    password = wtforms.PasswordField(
        'password',
        [wtforms.validators.InputRequired()]
    )


# ログインユーザー登録
class SignupForm(flask_wtf.FlaskForm):
    
    org_name = wtforms.StringField(
        'org_name',
        [wtforms.validators.InputRequired()]
    )
    member_code = wtforms.StringField(
        'member_code',
        [wtforms.validators.InputRequired()]
    )
    password = wtforms.PasswordField(
        'password',
        [wtforms.validators.InputRequired()]
    )


# 本の登録
class RegistBookForm(flask_wtf.FlaskForm):
    isbn = wtforms.StringField(
        'isbn',
        validators=[
            wtforms.validators.Regexp("^([0-9]{10}|[0-9]{13})$", message="ISBNは10桁または13桁の整数を入力してください。"),
            wtforms.validators.Length(min=10, max=13)
        ]
    )


# 本の変更
class EditBookForm(flask_wtf.FlaskForm):
    num_of_same_books = wtforms.IntegerField(
        'num_of_same_books',
        [wtforms.validators.InputRequired()]
    )


# 本を借りる
class BorrowBookForm(flask_wtf.FlaskForm):
    book_id = wtforms.HiddenField(
        'book_id',
        [wtforms.validators.DataRequired()]
    )


# ジャンルの登録
class RegistGenreForm(flask_wtf.FlaskForm):
    parent_genre_id = wtforms.StringField(
        'parent_genre_id'
    )
    genre_name = wtforms.StringField(
        'genre_name',
        [wtforms.validators.InputRequired()]
    )
