# Notes

## [Chapter 1 & 2: Hello World and Template](</README_01.md>)

## [Chapter 3: Web Forms](</Readme_03.md>)

## Ch4: Database

### SQLAlchemy

安裝 [SQLAlchemy](<https://docs.sqlalchemy.org/en/13/orm/tutorial.html>) & [Flask-SQLAlchemy](<https://flask-sqlalchemy.palletsprojects.com/en/2.x/>) 這兩個套件, 提供一種管理 SQL databae 的套件, 將一些 SQL 語法用 classes, objects 的思維來包裝. 

安裝 `Flask-Migrate` & `Alembic` 來提供資料庫遷移的工具.

### Database 簡單配置

1. 透過讀取環境變數 `DATABASE_URL` 獲得資料庫路徑.

2. 關閉 Flask-SQLAlchemy 提供的監控資料庫變更功能.

```python
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    '''
    Flask app config class.
    '''
    ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ...
```

### 生成 Flask-SQLAlchemy, Flask-Migrate

在 app/__init_.py 中生成這兩個套件.

```python
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
```

`models` 會在後面介紹.

### Database Models

一個 model 就是 SQL DB 中的 table.

先建立 User model, 帶有 4 個屬性:

1. id (integer)
2. username (varchar)
3. email (varchar)
4. password_hash (varchar)

#### Create Models

```python
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f'<User {self.username}>'
```

### How to maintain databse migration

對 SQL DB 而言, 每一次的結構更新或變更(尤其是在開發的過程)在沒有其他工具支持時, 只能額外寫個工具讀出再寫入. Alembic (Flask-Migrate) 解決了這個麻煩事, 他會紀錄每次資料庫結構的變更以及遷移腳本.

Flask-migrate 提供一個 flask 子命令來管理這個 migration database.

```cmd
$ flask db --help
```

初使化 migration database: 執行完畢後會建立 `migrations` 目錄.

```cmd
$ flask db init
```

執行第一次遷移紀錄, 以就是記錄這一次資料庫的變更, 建立一個新 table. Alembic 會自動去偵測差異. `-m` 這個參數只是會將過程呈現出簡單的描述. 而這命令只是產生 2 個 scripts - `upgrade` & `downgrade` - 被放在 `migrations/versions/xxxx_users_table.py` 中.

```cmd
$ flask db migrate -m "users table"
```

執行遷移, 但要注意的是, 如果要使用 `MySQL` or `PostgreSQL`, db file 必須先被建立, 因為 Alembic 預設是會自動建立 `SQLite` db (假如沒看到 db file), 接著執行下面命令.

```cmd
$ flask db upgrade
```

### 建立第二個資料庫 model

這次是建立一個 post table, 帶有五個屬性, 一樣放在 `models.py` 中:

1. id （Integer)
2. title (Varchar)
3. body (Varchar)
4. timestamp (Datetime)
5. user_id (Integer)

```python
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return f'<Post {self.title}>'
```

在 timestamp 的屬性生成中, `datetime.utcnow` 是以一個 function被傳入.

#### The relationship of Users & Posts table

這是一個一對多的關係, 一位 user 可以有多個 post, 但一個 post 只屬於一位 user.

在 `class Post` 已描述每一個 post 只屬於一位 user 的關係.

```python
class Post(db.Model):
    ...
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    ...
```

以下是一位 user 有多個 post 的關係:

```python
class User(db.Model):
    ...
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    ...
```

第一個參數是所關聯的表格模塊名稱. 第二個參數是 User 在 Post 中被引用的名稱, `post.author`. 第三個參數是定義資料庫查詢的方式. 

### migrate again

因為增加了新 table, 和 table 之間的關係, 所以在做一次 migration.

```cmd
$ flask db migrate -m "posts table"
$ flask db upgrade
```

執行完後, 資料庫就有了新的資料庫模塊定義.

### 測試剛剛建立的表

剛剛的命令只是將 tables schema 建立完畢, 然後進入 python command line 來處理相關的資料建立, 搜索, 刪除.

[Flask-Sqlalchemy](<https://flask-sqlalchemy.palletsprojects.com/en/2.x/>)

#### 建立新的 user post

```python
u = User(username='jon', email='jon@gmail.com')
db.session.add(u)
p = Post(title="Test Title", body="First post body!", author=u)
db.session.add(p)
db.session.commit()
```

#### 獲取所有資料, 以及依 primary key 獲取特定資料

```python
users = User.query.all()
for u in users:
    print(u.username, u.email)

posts = Post.query.get(2)
```

#### 依順序獲取資料

```python
User.query.order_by(User.username.desc()).all()
```

#### 刪除資料

```python
users = User.query.all()
for u in users:
    db.session.delete(u)
db.session.commit()
```

### flask shell

Flask 另外提供一個子命令, `flask shell`, 執行完畢後會直接將 Python interpreter 呼叫起來, 和直接呼叫的差別是, `flask shell` 會預設將 app (Flask) 載入.

Flask 也提供方式額外增加載入的物件:

```python
from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
```

這個方式預設導入一些 class, 方便調適.

## CH5: [User Logins](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins>)

### Password hashing

如何將 password 加密儲存? 利用 [Werkzeug](<https://palletsprojects.com/p/werkzeug/>) 這個隨著安裝 Flask 一起被安裝的包, 提供了 [generate_password_hash](<https://werkzeug.palletsprojects.com/en/0.15.x/utils/#werkzeug.security.generate_password_hash>) & [check_password_hash](<https://werkzeug.palletsprojects.com/en/0.15.x/utils/#werkzeug.security.check_password_hash>) 這兩個 function. 

利用 `generate_password_hash` & `check_password_hash` 為 models.User (資料庫 User table) 增加兩個 method: `set_password` & `check_password`. 

`set_password`: 將密碼轉換成 hash code 儲存進資料庫

`check_password`: 將使用者輸入的密碼和資料庫中相對的 hash code 比對, 內容相同則 true, 反之亦然.

```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    ...
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### 介紹 [Flask-Login](<https://flask-login.readthedocs.io/en/latest/>)

提供的主要功能:

1. 管理用戶登入狀態
2. 提供`記住我`的功能

模塊初始化如下:

```python
from flask_login import LoginManager

app = Flask(__name__)
...
login = LoginManager(app)
```

### 使用 Flask-Login 的額外準備工作

Flask-Login 最主要的函數是 `login_user()` & `logout_user()`, 以及一個全域的變數 `current_user`. 

在呼叫 `login_user()` 時, 必須要傳入一個以以下 3 個屬性及一個 function 實作的物件:

1. `is_authenticated`: 用戶是否通過登入認證, return true or false.

2. `is_active`: 用戶是通過輸入用戶名和密碼登入(actived: true), 或是利用`記住我`的功能登入(non-actived: false)

3. `is_anonymous`: 匿名/特殊用戶(true)或一般用戶(false)

4. `get_id()`: 回傳使用者的 id(字符串)

所以自訂的 user class 必須有定義以上四個 function, 以及定義一個屬性 - `id`.

Flask-Login 額外提供了一個類, `flask_login.UserMixin`, 都預先實作了這四個 callback function, 我們可以直接繼承這個類就有了這四個 function. 在 Flask-Login 的源碼中, 將使用者定義兩類:

1. `UserMixin`: 有註冊的使用者, `is_anonymous()` 回傳 false, `is_authenticated()` & `is_active()` 都回傳 true.

2. `AnonymousUserMixin`: 沒註冊的, `is_anonymous()` 回傳 true, `is_authenticated()` & `is_active()` 都回傳 false.

當在呼叫 login_user() 之前, Flask-Login 的源碼是將 `AnonymousUserMixin` 的物件設成 `current_user`, login_user() 之後就改成所傳入的資料.

```python
...
from flask_login import UserMixin

class User(UserMixin, db.Model):
    ...
```

### 實作一個回調函數獲取特定 id 的 user

因為 Flask-Login 不知道要如何處理資料庫的事物, 所以設計了這個回調函數, `@login.user_loader`, 由 Flask-Login 傳入 id, 然後 flask app 依據 id 來生成 user object.

```python
from app import login
# ...

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
```

個人納悶的地方: 在呼叫 `login_user()` 時已經傳入 user object 了, 為何還要另一個回調函數來獲取 user object? 這就要深入 Flask-Login 源碼了解.

### Logging Users in

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

### Logging Users Out

```python
# ...
from flask_login import logout_user

# ...

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
```

#### 依據 current_user.is_anonymous 來決定呈現 login/logout 字段

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

### 要求用戶登入

Flask_Login 提供了一個功能, 強制用戶在查看應用的特定頁面之前登入. 首先必須先讓 Flask_Login 知道登入頁面是哪一個:

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

在不考慮惡意攻擊的情況下, 是可以不用呼叫 `url_parse(next_page).netloc != ''`. 駭客只要在 next 後面加上其他惡意 URL, eg. `/login?next=http://www.othersurl.com`. 

所以用 `Werkzeug.url_parse().netloc` 來判斷 next_page 是否是相對路徑或絕對路徑.

### 如何渲染已登入的使用者資料

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

### 用戶註冊

如何自定義驗證器? 添加 `validate_<field_name>` 的方法, `WTForm` 就會認定這自定義的驗證器. 本案例是要驗證 username/ email 是否存在, 若存在則丟出一個 `ValidationError`.

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

## Others: Flask 提供的元件

1. [Command Line Interface](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#command-line-interface>)

2. [URL Route Registration](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#url-route-registrations>) 

3. [Class-Based Views](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#class-based-views>)

4. [Signals](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#signals>)

5. [Useful Internals](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#useful-internals>)

6. [Stream Helpers](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#stream-helpers>)

7. [Configuration](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#configuration>)

8. [Template Rendering](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#template-rendering>)

9. [Tagged JSON](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#tagged-json>)

10. [JSON Support](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#module-flask.json>)

11. [Message Flashing](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#message-flashing>)

12. [Useful Functions and Classes](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#useful-functions-and-classes>)

13. [Application Globals](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#application-globals>)

14. [Test CLI Runner](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#test-cli-runner>)

16. [Test Client](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#test-client>)

17. [Session Interface](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#session-interface>)

18. [Sessions](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#sessions>)

19. [Response Objects](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#response-objects>)

20. [Incoming Request Data](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#incoming-request-data>)

21. [Blueprint Objects](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#blueprint-objects>)

22. [Application Object](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#application-object>)
