import flask_wtf
import wtforms

# ログインフォーム
class LoginForm(flask_wtf.FlaskForm):
    org_id = wtforms.IntegerField(
        'org_id',
        [wtforms.validators.DataRequired()]
    )
    member_code = wtforms.StringField(
        'member_code',
        [wtforms.validators.DataRequired()]
    )
    password = wtforms.PasswordField(
        'password',
        [wtforms.validators.DataRequired()]
    )

# 本の登録
class RegistBookForm(flask_wtf.FlaskForm):
    isbn = wtforms.IntegerField(
        'isbn',
        [wtforms.validators.DataRequired()]
    )
    book_name = wtforms.StringField(
        'book_name',
        [wtforms.validators.DataRequired()]
    )
