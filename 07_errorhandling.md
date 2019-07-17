# [CH7: Error Handling](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling>)

## 如何打開 debug mode ?

透過設定環境變數 `FLASK_DEBUG`:

```cmd
export FLASK_DEBUG=1
```

當再次呼叫 `flask run` 時, 終端畫面還會額外呈現出 `Debugger PIN` 的資訊, 這資料是給開發者在瀏覽器上直接進入 debug 時, 需要輸入的安全手段.

flask debug mode 在瀏覽器中坎入了 python 直譯器, 可讓開發者直接操作, 方便檢測相關的變數.

flask debug 打開後, 也提供了 reloader. 當 flask run 起來後, 當修改代碼後, flask 會自動重啟.

## 特製化錯誤頁面(404, 500,...)

### 增加新的 errors view function

利用 `@app.errorhandler` 定義新的錯誤處理器. 將所有的錯誤處理統一放在 `errors.py` 中

```python errors.py
from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
```

特別注意的是 return 要回傳第二個參數, 所有的 view function 其實都要回傳兩個參數, 在 `routes.py` 中的 view function 雖然只回傳一個參數, 但隱含回傳第二個參數是 200.

### 增加 error html page

```html 404.html
{% extends "base.html" %}

{% block content %}
    <h1>File Not Found</h1>
    <p><a href="{{ url_for('index') }}">Back</a></p>
{% endblock %}
```

```html 500.html
{% extends "base.html" %}

{% block content %}
    <h1>An unexpected error has occurred</h1>
    <p>The administrator has been notified. Sorry for the inconvenience!</p>
    <p><a href="{{ url_for('index') }}">Back</a></p>
{% endblock %}
```

### 將這些新的 error handler 註冊成功

只要在 `app/__init__.py` 中引入 `errors.py`

```python __init__.py
# ...

from app import routes, models, errors
```

## Sending Errors by Email

當 flask app 發生任何的 error 可以透過以下方式將 error report 透過郵件方式寄出.

### 獲取系統的 mail server 資訊

在 `config.py` 中讀取 mail server 的環境變數

```python config.py
class Config(object):
    #...
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['brad.lee.tw@outlook.com']
```

如果系統中沒有 mail server (表示沒有 MAIL_SERVER 這個環境變數), 這個功能也就不執行.

### 打包 log

利用 Python's `logging` package 提供的 `SMTPHandler` 寄出郵件:

```python __init__.py
import logging
from logging.handlers import SMTPHandler

#...
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'],
            subject='Microblog Failure',
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
```

將相關的 mail server 資訊填入 `SMTPHandler` 後, 設定 logging level, 再將此物件透過 `flask.logger.addHandler()` 加入.

這裡的設定是只有在 `FLASK_DEBUG` 關閉且系統存在 mail server, 此功能才有作用.

### 如果開發的系統還沒有 mail server, 如何測試 ?

有兩種方法:

#### Python SMTP module

利用 SMTP debuggin server 這個假郵件系統. 執行以下命令:

```cmd
python -m smtpd -n -c DebuggingServer localhost:8025
```

當然要將環境變數設成 `export MAIL_SERVER=localhost` & `export MAIL_PORT=8025`, 而且要 `export FLASK_DEBUG=0`

#### 利用外部郵件系統傳送郵件

##### 利用 QQ Mail 來當作郵件系統

首先 QQ Mail 要打開 `POP3/SMTP` & `IMAP/SMTP` 這兩個服務.

設定以下的資料到環境變數:

- `MAIL_SERVER`: "smtp.qq.com"
- `MAIL_PORT`: 587
- `MAIL_USERNAME`: "brad.lee.tw@qq.com"
- `MAIL_PASSWORD`: "授權碼"
- `MAIL_USE_TLS`: 1

特別注意 `MAIL_PASSWORD` 不是直接填入郵箱的密碼, 而是輸入在 QQ Mail server 獲得的授權碼, 這是和其他郵件系統不同的部分.

另一個注意的是在 `SMTPHandler()` 中傳入的 `fromaddr` 參數, 在 QQ Mail 中必須要設成 `MAIL_USERNAME`, 不然就會發生 error.

```python __init__.py
#...
if not app.debug:
    #...
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_USERNAME'],
            toaddrs=app.config['ADMINS'],
            subject='Microblog Failure',
            credentials=auth,
            secure=secure
        )
        #...
```

## Logging to a File

只透過郵件傳送 log 是不夠的, 我們需要完整紀錄 flask app 運行狀況. 透過 Python's `logging` package 提供的 `RotatingFileHandler` 來做.

```python __init__.py
from logging.handlers import SMTPHandler, RotatingFileHandler
#...

if not app.debug:
    #...
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
```

## Fixing the Duplicate Username Bug

在 `EditProfileForm()` 中新增一個 validator , 用來判斷新輸入的 username 是否已經存在, 但必須額外先記錄原先的 usernmae.

```python forms.py
class EditProfileForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
```

```python routes.py
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # ...
```