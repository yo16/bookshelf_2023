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
    description = wtforms.TextAreaField(
        'description'
    )
    num_of_same_books = wtforms.IntegerField(
        'num_of_same_books'
    )


# 本を借りる
class BorrowBookForm(flask_wtf.FlaskForm):
    book_id = wtforms.HiddenField(
        'book_id',
        [wtforms.validators.DataRequired()]
    )


# 本を返す
class ReturnBookForm(flask_wtf.FlaskForm):
    book_id = wtforms.HiddenField(
        'book_id',
        [wtforms.validators.DataRequired()]
    )


# ノートを取る
class TakeANoteForm(flask_wtf.FlaskForm):
    book_id = wtforms.HiddenField(
        'book_id',
        [wtforms.validators.DataRequired()]
    )
    note = wtforms.TextAreaField(
        'note',
        [wtforms.validators.InputRequired()]
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


# メンバーの追加
class RegistMemberForm(flask_wtf.FlaskForm):
    method = wtforms.HiddenField(
        'method',
        [wtforms.validators.InputRequired()]
    )
    reg_member_code = wtforms.StringField(
        'reg_member_code',
        [wtforms.validators.InputRequired()]
    )
    reg_member_name = wtforms.StringField(
        'reg_member_name',
        [wtforms.validators.InputRequired()]
    )
    reg_password = wtforms.StringField(
        'reg_password',
        [wtforms.validators.InputRequired()]
    )
    reg_is_admin = wtforms.HiddenField(
        'reg_is_admin'
    )


# メンバーの変更
class EditMemberForm(flask_wtf.FlaskForm):
    method = wtforms.HiddenField(
        'method',
        [wtforms.validators.InputRequired()]
    )
    edit_member_id = wtforms.IntegerField(
        'edit_member_id',
        [wtforms.validators.InputRequired()]
    )
    edit_member_name = wtforms.StringField(
        'edit_member_name',
        [wtforms.validators.InputRequired()]
    )
    edit_member_code = wtforms.StringField(
        'edit_member_code',
        [wtforms.validators.InputRequired()]
    )
    edit_password = wtforms.StringField(
        'edit_password'
    )
    edit_is_admin = wtforms.HiddenField(
        'edit_is_admin'
    )
    edit_is_enabled = wtforms.HiddenField(
        'edit_is_enabled'
    )


# メンバーの削除
class DeleteMemberForm(flask_wtf.FlaskForm):
    method = wtforms.HiddenField(
        'method',
        [wtforms.validators.InputRequired()]
    )
    del_member_id = wtforms.IntegerField(
        'del_member_id',
        [wtforms.validators.InputRequired()]
    )

