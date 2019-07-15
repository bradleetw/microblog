# [Ch4: Database](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database>)

## SQLAlchemy

安裝 [SQLAlchemy](<https://docs.sqlalchemy.org/en/13/orm/tutorial.html>) & [Flask-SQLAlchemy](<https://flask-sqlalchemy.palletsprojects.com/en/2.x/>) 這兩個套件, 提供一種管理 SQL databae 的套件, 將一些 SQL 語法用 classes, objects 的思維來包裝. 

安裝 `Flask-Migrate` & `Alembic` 來提供資料庫遷移的工具.

## Database 簡單配置

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

## 生成 Flask-SQLAlchemy, Flask-Migrate

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

## Database Models

一個 model 就是 SQL DB 中的 table.

先建立 User model, 帶有 4 個屬性:

1. id (integer)
2. username (varchar)
3. email (varchar)
4. password_hash (varchar)

### Create Models

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

## How to maintain databse migration

對 SQL DB 而言, 每一次的結構更新或變更(尤其是在開發的過程)在沒有其他工具支持時, 只能額外寫個工具讀出再寫入. Alembic (Flask-Migrate) 解決了這個麻煩事, 他會紀錄每次資料庫結構的變更以及遷移腳本.

Flask-migrate 提供一個 flask 子命令來管理這個 migration database.

```cmd
flask db --help
```

初使化 migration database: 執行完畢後會建立 `migrations` 目錄.

```cmd
flask db init
```

執行第一次遷移紀錄, 以就是記錄這一次資料庫的變更, 建立一個新 table. Alembic 會自動去偵測差異. `-m` 這個參數只是會將過程呈現出簡單的描述. 而這命令只是產生 2 個 scripts - `upgrade` & `downgrade` - 被放在 `migrations/versions/xxxx_users_table.py` 中.

```cmd
flask db migrate -m "users table"
```

執行遷移, 但要注意的是, 如果要使用 `MySQL` or `PostgreSQL`, db file 必須先被建立, 因為 Alembic 預設是會自動建立 `SQLite` db (假如沒看到 db file), 接著執行下面命令.

```cmd
flask db upgrade
```

## 建立第二個資料庫 model

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

### The relationship of Users & Posts table

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

## migrate again

因為增加了新 table, 和 table 之間的關係, 所以在做一次 migration.

```cmd
$ flask db migrate -m "posts table"
$ flask db upgrade
```

執行完後, 資料庫就有了新的資料庫模塊定義.

## 測試剛剛建立的表

剛剛的命令只是將 tables schema 建立完畢, 然後進入 python command line 來處理相關的資料建立, 搜索, 刪除.

[Flask-Sqlalchemy](<https://flask-sqlalchemy.palletsprojects.com/en/2.x/>)

### 建立新的 user post

```python
u = User(username='jon', email='jon@gmail.com')
db.session.add(u)
p = Post(title="Test Title", body="First post body!", author=u)
db.session.add(p)
db.session.commit()
```

### 獲取所有資料, 以及依 primary key 獲取特定資料

```python
users = User.query.all()
for u in users:
    print(u.username, u.email)

posts = Post.query.get(2)
```

### 依順序獲取資料

```python
User.query.order_by(User.username.desc()).all()
```

### 刪除資料

```python
users = User.query.all()
for u in users:
    db.session.delete(u)
db.session.commit()
```

## flask shell

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
