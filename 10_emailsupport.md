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

