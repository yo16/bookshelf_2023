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