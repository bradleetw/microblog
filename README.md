# Notes

## [Chapter 1 & 2: Hello World and Template](</README_01.md>)

## [Ch3: Web Forms](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms>)

### 3.1 Flask App 的配置

Flask 有提供幾種方式來設定配置, 如下. [flask.config](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#configuration>).

#### Dictionary style of app.config
透過 key/value 的方式來設定.
```python
    app.config['SECRET_KEY'] = 'dev'
    app.config['DATABASE'] = os.path.join(app.instance_path, 'flaskr.sqlite')
```

#### [flask.config.from_mapping()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_mapping>)

```python
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
```

#### [flask.config.from_pyfile()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_pyfile>)

透過另外的檔案來設定配置. 首先在 app 目錄下建立 `config.cfg` (檔名自定義), 其內容用 python 語法.

```python
SECRET_KEY = "devfortesting"
PP_KEY_TESTING = "Just for testing."
```

載入 `config.cfg` 的方式, 也可以是絕對路徑, 若沒填就表示在`app/`底下:

```python
from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
```

#### [flask.config.from_json()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_json>)

另一種透過 json file 來設定配置的方法, 一樣在 app 目錄下建立 `config.json` (檔名自定義).

```json
{
    "SECRET_KEY": "devfortesting",
    "PP_KEY_TESTING": "Just for testing."
}
```

```python
from flask import Flask

app = Flask(__name__)
app.config.from_json('config.json')
from app import routes
```

#### [flask.config.from_object()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_object>)

也可以直接透過 python 的 class, or module 來輸入配置設定. 

##### module

就像建立一個 python module 一樣的方式, 現在 `app` 下建立一個目錄, `default_cfg` (目錄名自定義), 並在此目錄下也建立 `__init__.py`, 然後在此檔案中引用如下:

```python
SECRET_KEY = "devfortesting"
PP_KEY_TESTING = "Just for testing."
```

透過 from_object() 設定

```python
from flask import Flask

app = Flask(__name__)
app.config.from_object('app.default_cfg')
from app import routes
```

##### class

建立一個 class 如下:

```python
import os

class Config(object):
    '''
    Flask app config class.
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'devfortesting'

    PP_KEY_TESTING = 'Just for testing.'
```

一樣利用 from_object 來導入配置.

```python
from flask import Flask
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

from app import routes
```

### 3.2 設計使用者登入頁面

利用 [wtforms](<https://wtforms.readthedocs.io/en/stable/index.html>) & [Flask-WTF](<https://flask-wtf.readthedocs.io/en/stable/index.html>) 這兩個第三方的套件, 可以方便打造 form 頁面. 

#### Web form class

將這個頁面的 web form class 放到一個獨立的 py file, forms.py

```python
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField(label='User Name', validators=[DataRequired(message='Need user name.')])
    password = PasswordField(label='Password', validators=[DataRequired(message='Need password')])
    remember_me = BooleanField(label='Remember Me')
    submit = SubmitField(label='Sign In')
```

#### html template

當然這只是骨架, 必須再加上 HTML, 所以以下就是其 html.

```html
{% extends "base.html" %}

{% block content%}
    <h1>{{ title }}</h1>
    <form action="" method="post" novalidate>
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}
            {% for error in form.username.errors %}
                <span style="color: red;">[{{ error }}]</span>
            {% endfor %}        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}
            {% for error in form.password.errors %}
                <span style="color: red;">[{{ error }}]</span>
            {% endfor %} </p>
        </p>
        <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

在此 html 中的 `form` 是我們待會在 router 裡呼叫 render_template() 時會定義到. 其實就是將前面定義的 `LoginForm` 所要生成的一個物件. 而 `form.usernmae`, `form.password`, `form.remember_me`, and `form.submit` 其實也就是 LoginForm 的屬性.

比較特別的是 `{{ form.hidden_tag() }}` 這一句, 主要是為了避免這個 form 遭受 CSRF 的攻擊. 而這是 `Flask-WTF` 所提供的功能.

#### Render views

再加上 `login()`, 並在其內將 `LoginForm` 生成, 並透過 `render_template()` 和 html 做連接. 如此一個 user login page 就完成了.

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = {'username': 'Brad Lee'}
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            f'Login requested for user {form.username.data}, \
                remember_me = {form.remember_me.data}'
        )
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', user=user, form=form)
```

`form.validate_on_submit()` 是依據 `LoginForm` 裡設定的 `validators`, 判斷其結果是否正確. 

`flash()` 只是一個簡單類似 `printf` 的輸出功能, 並需要 html 頁面搭配才能真正輸出. 直接加入以下片段到 html 頁面.

```html
    {% with messages = get_flashed_messages() %}
    {% if messages %}
    <ul>
        {% for message in messages %}
        <li>{{ message }}</li>
        {% endfor %}
    </ul>
    {% endif %}
    {% endwith %}
```

## Database

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
