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
