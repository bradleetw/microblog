# [CH10: Email support](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support>)

這章節主要是增加重置密碼的功能, 透過郵件傳送重置密碼的鏈結.

## [Flask-Mail](<https://pythonhosted.org/Flask-Mail/>)

```command
pip install flask-mail
```

### Flask-mail configuration

而相關的 mail 配置在 [CH7: Error Handling](</07_errorhandling.md>) 已經設定完畢.

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

而在 [Flask-mail](<https://pythonhosted.org/Flask-Mail/#configuring-flask-mail>) 中還可以多設定其他的.

- **MAIL_SERVER** : default ‘localhost’
- **MAIL_PORT** : default 25
- **MAIL_USE_TLS** : default False
- **MAIL_USE_SSL** : default False
- **MAIL_DEBUG** : default app.debug
- **MAIL_USERNAME** : default None
- **MAIL_PASSWORD** : default None
- **MAIL_DEFAULT_SENDER** : default None
- **MAIL_MAX_EMAILS** : default None
- **MAIL_SUPPRESS_SEND** : default app.testing
- **MAIL_ASCII_ATTACHMENTS** : default False

### Flask-mail initial

```python __init__.py
# ...
from flask_mail import Mail

# ...
mail = Mail(app)
```

### 簡單的 email 框架

透過 flask-mail 提供的 Message 將 email 的相關屬性填入.

```python email.py
from flask_mail import Message
from app import mail, app


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
```

## 重置密碼的入口

相關的入口是放在 登入頁面中 的一個鏈結, 該鏈結會跳到我們新增的另一個新頁面, `reset_password_request`.
這個頁面主要是讓使用者輸入使用者的郵件地址, 並將重置郵件傳送到該郵箱.

```html login.html
<!-- ... -->
        <p>New User? <a href="{{ url_for('register') }}">Click to Register!</a></p>
        <p>Forgot Your Password? <a href="{{ url_for('reset_password_request')}}">Click to Reset It</a></p>
<!-- ... -->
```

### reset_password_request 新頁面

本頁面主要是讓使用者輸入使用者的郵件地址, 透過使用者按下傳送鍵後驅動將重置郵件傳送到該郵箱.

```html reset_password_request.html
{% extends "base.html" %}

{% block content %}
<h1>Reset Password</h1>
<form action="" method="post">
    {{ form.hidden_tag() }}
    <p>
        {{ form.email.label }}<br>
        {{ form.email(size=64) }}<br>
        {% for error in form.email.errors %}
        <span style="color: red;">[{{ error }}]</span>
        {% endfor %}
    </p>
    <p>{{ form.submit() }}</p>
</form>
{% endblock %}
```

因為這也是一個 Web 表單, 所以也增加新的 FlaskForm.

```python forms.py
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
```

然後增加新的路由. 因為本重置密碼主要是針對已經忘記的使用者, 所以已經登入的使用者就無法使用重置密碼, 也就是要先登出後才能進行重置密碼.

當使用者填好郵箱地址, submit 回來, 我們要依據 mail address 查找資料庫來獲取相對應的 User. 若有找到, 則呼叫另一個新的 function, `send_password_reset_mail()`, 傳送郵件, 並將該 user 的資料傳入.

```python routes.py
@app.route('/reset_password_request', methods=['POST', 'GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instruction to reset your password')
        else:
            flash(f'There is no user with email, {form.email.data}')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)
```

### 寄送 password reset email

透過 `send_email()` 填入主題, 寄送者, 接收者, 以及內容 等相關欄位, 郵件就可以寄送出去.

```python email.py
# ...
from flask import render_template

# ...
def send_password_reset_email(user):
    send_email('[Microblog] Reset your password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user),
               html_body=render_template('email/reset_password.html',
                                         user=user))

```

特別解釋郵件的內容, 分別填入 text & html 格式, 經由 `render_template()` 將使用者的資訊填入.

```text reset_password.txt
Dear {{ user.username }},

To reset your password click on the following link:

{{ url_for('reset_password', username=user.uername, _external=True) }}

If you have not requested a password reset simply ignore this message.

Sincerely,

The Microblog Team
```

```html reset_password.html
<p>Dear {{ user.username }},</p>
<p>
    To reset your password
    <a href="{{ url_for('reset_password', username=user.username, _external=True) }}">
        click here
    </a>.
</p>
<p>Alternatively, you can paste the following link in your browser's address bar:</p>
<p>{{ url_for('reset_password', username=user.username, _external=True) }}</p>
<p>If you have not requested a password reset simply ignore this message.</p>
<p>Sincerely,</p>
<p>The Microblog Team</p>
```

## 基本版本的問題

上面的動作已經完成發送 reset password email, 重設 password 的功能.

但目前的功能存在很大問題, 重置密碼鏈結是 `http://127.0.0.1:5000/reset_password/username`, 也就是一般的使用者可以不用等到收到郵件, 只要直接將鏈結的後綴改成任意的使用者名稱, 就可以直接更改任意的使用者密碼.

所以接著要將後綴的使用者名稱的設計, 改成將使用者名稱加密的方法. 此處介紹了 [**Json Web Toekn**](<https://jwt.io/>) (JWT) 業界常用的方式, 應用在 Single Sign On. 
簡單來說就是將輸入的 JSON 資料, 經過私密鑰匙的處理後產生的一串亂碼字串, 收到該字串後, 再依照原私密鑰匙即可恢復得到 JSON 資料.

雖然是一串亂碼, 但還是很容易被解讀 JSON 資料出來, 例如透過 [JWT Debgger](<https://jwt.io/#debugger>) 就可以看到.
所以若再傳送的過程中被其他駭客攔截更改, 只要私密鑰匙被猜到, 就會像基本版本一樣, 輕易的被駭客搞爛系統, 將所有的使用者密碼變更. 所以這個方法的保護等級取決於私密鑰匙的等級.

### [Pyjwt package](<https://pyjwt.readthedocs.io/en/latest/index.html>)

JWT 提供了很多語言的 Package, 如: Python, Java, Go, .Net, ... 這裡選擇 Python version , [Pyjwt](<https://github.com/jpadilla/pyjwt/>).

```command
pip install pyjwt
```

### 透過 jwt 執行加密 & 解密

Pyjwt package 主要會用到的是 `encode()` & `decode()` 這兩個功能.

基本的使用方法如下:

```python
import jwt
token = jwt.encode({'A': 'B'}, 'myprivatekey', algorithm='HS256')
tmp = jwt.decode(token, 'myprivatekey', algorithm='HS256')
```

**jwt.encode** 第一個參數, 直接放入 JSON 型態的資料, 而 **jwt.decode** 第一個參數則是傳入 encode 後的 token.

第二個參數傳入 private key, 在 Flask app 的應用中, 我們可以直接用 `app.config['SECRET_KEY']`.

第三個參數傳入使用編碼的種類, 這裡直接使用 `HS256`, [其他種類](<https://pyjwt.readthedocs.io/en/latest/algorithms.html>).

#### 超時失效

JWT 的[定義](<https://www.iana.org/assignments/jwt/jwt.xhtml>)中, enocde 第一個參數的 JSON 除了可以放入要傳輸的資料, 也定義了一些特定功能的參數, 這裡只說明常用的**超時失效**.

只要多加入一組 `'exp': time`, 當在 jwt.decode() 時會直接判斷時間有無超時. 這是最常用的設定.

## 鏈結加密版本

原本的版本的重置密碼鏈結是 `http://127.0.0.1:5000/reset_password/username`, 這裡將 `username` 改成 `user.id`. 

接著是在 User 增加 `get_reset_password_token()` & `verify_reset_password_token()`.

### encode reset password url

傳入超時的時間間隔 expires_in:

```python models.py
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {
                'reset_password': self.id,
                'exp': time() + expires_in
            },
            app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
```

要特別注意的是, jwt.encode() 所產生的字串要再將其轉成 `utf-8`.

### decode reset password url

```python models.py
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithm='HS256')['reset_password']
        except:
            return
        return User.query.get(id)
```

將依獲得的 user.id 查找 User.

### 更改 email.py 種的 send_password_reset_email()

獲得 token 字串, 超時時間設定為 5 分鐘, 並傳入郵件中

```python email.py
def send_password_reset_email(user):
    token = user.get_reset_password_token(expires_in=300)
    send_email('[Microblog] Reset your password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template(
                   'email/reset_password.txt',
                   user=user,
                   token=token),
               html_body=render_template(
                   'email/reset_password.html',
                   user=user,
                   token=token))
```

### 依據 token 更改 reset_password.txt & reset_password.html 中的鏈結

```html reset_password.html
<!-- ... -->
    To reset your password
    <a href="{{ url_for('reset_password', token=token, _external=True) }}">
        click here
    </a>.
</p>
<p>Alternatively, you can paste the following link in your browser's address bar:</p>
<p>{{ url_for('reset_password', token=token, _external=True) }}</p>
<!-- ... -->
```

```text reset_password.txt
...
To reset your password click on the following link:

{{ url_for('reset_password', token=token, _external=True) }}

If you have not requested a password reset simply ignore this message.
...
```

### 更改 routes.py 中的 reset_password()

改成接收 token, 並透過 `User.verify_reset_password_token()` 解譯出 user instance.

```python routes.py
@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    # ...
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    # ...
```

