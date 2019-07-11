# Notes

## [Chapter 1: Hello World](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world>)

基本的架構如下
```text
.
├── app
│   ├── __init__.py
│   └── routes.py
└── microblog.py
```

### 如何將 flask app 執行起來 ?

1. 先在環境變數中加入指定被 flask 執行的 app

```text
export FLASK_APP=microblog.py
```

2. 在命令咧執行 `$ flask run`

### 替代手動加入環境變數的方法

安裝 `python-dotenv`, 接著只要建立一個 `.flaskenv` 的檔案, 並在檔案中填入 `FLASK_APP=microblog.py`, 如此當執行 `$ flask run` 的時候就會找到相對的flask app 執行起來.

## [Ch2: Template](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates>)

Flask 是專注後台相關事務的框架, 對於用戶要看到的網頁, 因為是屬於 front-end 領域, 所以要利用其他的工具來完成 HTML/CSS/JS, 然後在這些 HTML 中`填入相關從 flask app 回傳獲得的資料`, 而如何預留空格, 以及如何填, Flask 就利用 [Jinja2](<http://jinja.pocoo.org/docs/2.10/>) 來當作其模板引擎, 將資料和 HTML 整合渲染成最後的網頁.

### 模板資料要放在何處?

Flask 會預設從 app 目錄下的 `tamplates` 目錄中讀取, 所以我們要先建立 tempaltes folder.

### 如何在 HTML 中預留要填入資料的變數

`Jinia2` 所認得的關鍵字 `{{ ... }}`, 在這符號內把它當成變數來看.

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>{{ title }} - microblog</title>
    </head>
    <body>
        Hello {{ user.username }} ~
    </body>
</html>
```

### 如何在 Flask app 中田入相對映的資料並渲染?

Flask 提供了 `render_template` 將網頁填入資料, 並渲染出來. 第一個參數就是網頁名稱, 當然 Flask 預設是從 `templates` 去找, 後面的參數就是相對的變數資料.

```python
from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Brad Lee'}

    return render_template('index.html', title='Home', user=user)
```

### Jinja 提供了簡單的 條件\循環 語法

#### [條件語法](<http://jinja.pocoo.org/docs/2.10/templates/#list-of-control-structures>)

可以依據 變數 內容來決定如何渲染. 關鍵字 `{% if %}`, `{% elif %}`, `{% else %}`, `{% endif %}`

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>
            {% if title %}
                {{ title }} - Microblog
            {% else %}
                Welcome to Microblog
            {% endif %}
        </title>
    </head>
    <body>
        Hello {{ user.username }} ~
    </body>
</html>
```

#### [循環語法](<http://jinja.pocoo.org/docs/2.10/templates/#line-statements>)

變數可以是 Array 傳入, 利用 `{% for %}`, `{% endfor %}` 來循環將所有資料渲染出來.

```python
@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Brad Lee'}
    post = [
        {'author': 'James', 'body': 'I am OK!'},
        {'author': 'Brad lee', 'body': 'Fine~~~'},
        {'author': 'Vivian', 'body': 'You are welcome'},
        {'author': 'Andy', 'body': 'No Problem!'}
    ]
    return render_template('index.html', title='Home', user=user, seq=post)
```

相對應的模板:

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>
            {% if title %}
                {{ title }} - Microblog
            {% else %}
                Welcome to Microblog
            {% endif %}
        </title>
    </head>
    <body>
        Hello {{ user.username }} ~
        <ul>
            {% for item in seq %}
                <li>{{ item.author }} says: {{ item.body }}</li>
            {% endfor %}
        </ul>
    </body>
</html>
```

### [模板繼承](<http://jinja.pocoo.org/docs/2.10/templates/#template-inheritance>)

在一個網站中, 不同的頁面就要各自有一個 HTML, 也就是要有一個獨立的模板, 所以假若你的網站有十個頁面, 就表示會有十個模板. 假若每個頁面有共通的頁面元素, 是可以提取出來, 然後利用 `Jinja2` 的 `模板繼承`功能來渲染.

我們可以將提取出來的父頁面模板取名為 `base.html`, 當然命名方法沒有一定. 然後透過`{% block content %}{% endblock %}`的語法, 留給繼承的子頁面來添加新的元素.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>
        {% if title %}
            {{ title }} - Microblog
        {% else %}
            Welcome to Microblog
        {% endif %}
    </title>
</head>
<body>
    <div>Microblog[Hello {{ user.username }} ]: <a href="/index">Home</a></div>
    <hr> 
    {% block content %}{% endblock %}
</body>
</html>
```

繼承的語法, `{% extends "base.html" %}`. 

```html
{% extends "base.html" %}

{% block content%}
    <ul>
        {% for item in seq %}
        <li>{{ item.author }} says: {{ item.body }}</li>
        {% endfor %}
    </ul>
{% endblock %}
```

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
