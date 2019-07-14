
# [Ch3: Web Forms](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms>)

## 3.1 Flask App 的配置

Flask 有提供幾種方式來設定配置, 如下. [flask.config](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#configuration>).

### Dictionary style of app.config

透過 key/value 的方式來設定.

```python
    app.config['SECRET_KEY'] = 'dev'
    app.config['DATABASE'] = os.path.join(app.instance_path, 'flaskr.sqlite')
```

### [flask.config.from_mapping()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_mapping>)

```python
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
```

### [flask.config.from_pyfile()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_pyfile>)

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

### [flask.config.from_json()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_json>)

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

### [flask.config.from_object()](<http://flask.pocoo.org/docs/1.0/api/?highlight=config#flask.Config.from_object>)

也可以直接透過 python 的 class, or module 來輸入配置設定. 

#### module

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

#### class

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

## 3.2 設計使用者登入頁面

利用 [wtforms](<https://wtforms.readthedocs.io/en/stable/index.html>) & [Flask-WTF](<https://flask-wtf.readthedocs.io/en/stable/index.html>) 這兩個第三方的套件, 可以方便打造 form 頁面. 

### Web form class

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

### html template

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

#### CSRF

比較特別的是 `{{ form.hidden_tag() }}` 這一句, 主要是為了避免這個 form 遭受 CSRF 的攻擊. 而這是 `Flask-WTF` 所提供的功能.

### Render views

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
