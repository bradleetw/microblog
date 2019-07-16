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

## Logging to a File

## Fixing the Duplicate Username Bug

##