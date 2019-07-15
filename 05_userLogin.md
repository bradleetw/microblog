# CH5: [User Logins](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins>)

## Password hashing

如何將 password 加密儲存? 利用 [Werkzeug](<https://palletsprojects.com/p/werkzeug/>) 這個隨著安裝 Flask 一起被安裝的包, 提供了 [generate_password_hash](<https://werkzeug.palletsprojects.com/en/0.15.x/utils/#werkzeug.security.generate_password_hash>) & [check_password_hash](<https://werkzeug.palletsprojects.com/en/0.15.x/utils/#werkzeug.security.check_password_hash>) 這兩個 function.

利用 `generate_password_hash` & `check_password_hash` 為 models.User (資料庫 User table) 增加兩個 method: `set_password` & `check_password`.

`set_password`: 將密碼轉換成 hash code 儲存進資料庫

`check_password`: 將使用者輸入的密碼和資料庫中相對的 hash code 比對, 內容相同則 true, 反之亦然.

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    #...
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

## 介紹 [Flask-Login](<https://flask-login.readthedocs.io/en/latest/>)

提供的主要功能:

1. 管理用戶登入狀態
2. 提供`記住我`的功能

模塊初始化如下:

```python
from flask_login import LoginManager

app = Flask(__name__)
#...
login = LoginManager(app)
```

## 使用 Flask-Login 的額外準備工作

Flask-Login 最主要的函數是 `login_user()` & `logout_user()`, 以及一個全域的變數 `current_user`.

在呼叫 `login_user()` 時, 必須要傳入一個以以下 3 個屬性(@property function)及一個 function 實作的物件:

1. `is_authenticated`: 用戶是否通過登入認證, return true or false.

2. `is_active`: 用戶是通過輸入用戶名和密碼登入(actived: true), 或是利用`記住我`的功能登入(non-actived: false)

3. `is_anonymous`: 匿名/特殊用戶(true)或一般用戶(false)

4. `get_id()`: 回傳使用者的 id(字符串)

所以自訂的 user class 必須有定義以上四個 function, 以及定義一個名稱為的 `id` 屬性.

Flask-Login 額外提供了一個類, `flask_login.UserMixin`, 都預先實作了這四個 callback function, 我們可以直接繼承這個類就有了這四個 function, 若有不一樣的使用情況, 可以直接覆寫掉特定 functio .

在 Flask-Login 的源碼中, 將使用者分成兩類:

1. `UserMixin`: 有註冊的使用者, `is_anonymous()` 回傳 false, `is_authenticated()` & `is_active()` 都回傳 true.

2. `AnonymousUserMixin`: 沒註冊的, `is_anonymous()` 回傳 true, `is_authenticated()` & `is_active()` 都回傳 false.

源碼中當在呼叫 login_user() 之前, Flask-Login 的源碼是將 `AnonymousUserMixin` 的物件設成 `current_user`, login_user() 之後就改成所傳入的資料.

```python
#...
from flask_login import UserMixin

class User(UserMixin, db.Model):
    #...
```

## 實作一個回調函數獲取特定 id 的 user

因為 Flask-Login 不知道要如何處理資料庫的事物, 所以設計了這個回調函數, `@login.user_loader`. 在實作這個回調函數時, Flask-Login 會傳入 id, 然後 flask app 依據 id 來生成(也許是從 database or others) user object.

```python
from app import login
# ...

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
```

個人納悶的地方: 在呼叫 `login_user()` 時已經傳入 user object 了, 為何還要另一個回調函數來獲取 user object? 應該是一個網站有多個頁面, 什麼時候使用者 request 其他頁面, 是無法確定的, 所以一直透過 login_user() 所傳入的 user object 來判斷會有風險, 所以利用這個回調函數可能可以減少風險. 要深入 Flask-Login 源碼了解.

## Logging Users in

1. 進入 /login url 時, 判斷 `current_user` 是不是已經登入成功, 若是, 直接轉到 /index url

2. 若還沒登入, 則渲染 login form page, 等待使用者輸入資料

3. 輸入資料的格式若不正確, 則停留在 login form page

4. 資料的格式正確, 則從資料庫找尋使用者資料, 若資料找不到則重新將頁面轉到 login form page

5. 若從資料庫找到資料, 則比對密碼正確與否, 若不正確則重新將頁面轉到 login form page

6. 資料若都正確, 則將資料傳入 `login_user()`, 並將頁面轉到 /index page

```python
# ...
from flask_login import current_user, login_user
from app.models import User

# ...

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
```

## Logging Users Out

```python
# ...
from flask_login import logout_user

# ...

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
```

### 依據 current_user.is_anonymous 來決定呈現 login/logout 字段

```html
    <div>
        Microblog:
        <a href="{{ url_for('index') }}">Home</a>
        {% if current_user.is_anonymous %}
        <a href="{{ url_for('login') }}">Login</a>
        {% else %}
        <a href="{{ url_for('logout') }}">Logout</a>
        {% endif %}
    </div>
```

## 要求用戶登入

Flask_Login 提供了一個功能, 強制用戶在查看應用的特定頁面之前登入. 首先必須先讓 Flask_Login 知道登入頁面是哪一個 function :

```python
# ...
login = LoginManager(app)
login.login_view = 'login'
```

透過 `@login_required` 來讓 Flask_login 知道哪個頁面是必須登入才能瀏覽:

```python
from flask_login import login_required

@app.route('/')
@app.route('/index')
@login_required
def index():
    # ...
```

登入成功後(或是匿名著要瀏覽必須登入頁面)頁面重新轉回到原來頁面, Flask_login 是透過在 URL 加上查詢字符串參數, eg. `/login?next=/index`. 所以登入成功後透過 `flask` 提供的 `request.args.get('next')` 來獲取要回去的頁面 URL.

```python
from flask import request
from werkzeug.urls import url_parse

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ...
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    # ...
```

在不考慮惡意攻擊的情況下, 是可以不用呼叫 `url_parse(next_page).netloc != ''`. 但是駭客只要在 next 後面加上其他惡意 URL, eg. `/login?next=http://www.othersurl.com`, 就可以導到其他的惡意網頁.

所以用 `Werkzeug.url_parse().netloc` 來判斷 next_page 是否是相對路徑或絕對路徑.

## 如何渲染已登入的使用者資料

利用 `current_user` 來獲取登入使用者的相關料:

```html
{% extends "base.html" %}

{% block content %}
    <h1>Hi, {{ current_user.username }}!</h1>
    {% for post in posts %}
    <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
    {% endfor %}
{% endblock %}
```

## 用戶註冊

如何定義新的驗證器? 添加 `validate_<field_name>` , `WTForm` 就會認定這自定義的驗證器. 本案例是要驗證 username/ email 是否存在, 若存在則丟出一個 `ValidationError`, 讓使用者重新輸入.

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

# ...

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
```
