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
