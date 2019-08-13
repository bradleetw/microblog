# [CH11: Facelift](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-facelift>)

這章節主要講述的是利用 [Bootstrap](<https://getbootstrap.com/docs/4.3/getting-started/introduction/>) 加上 [bootstrap-flask](<https://bootstrap-flask.readthedocs.io/en/latest/>) 來美化前端介面.

## Bootstrap

是由 Twitter 團隊推出的 CSS 框架, 目前版本已來到 4.3.1. 有兩種導入方式, 一種是直接將 bootstrap.min.css 相關檔案放到 local template 中, 另一種則是利用 CDN, 也就是載渲染網頁時直接到網路上的 CDN 先下載 相關的 css.

所謂的 CSS 框架, 其實是定義了許多關鍵值的值, 例如: 以下定義了 primary type button 相關外觀

```css
.btn-primary{color:#fff;background-color:#28b76b;border-color:#28b76b}
.btn-primary:hover{color:#fff;background-color:#219859;border-color:#1f8d53}
.btn-primary:focus,.btn-primary.focus{box-shadow:0 0 0 .2rem rgba(72,194,129,0.5)}
.btn-primary.disabled,.btn-primary:disabled{color:#fff;background-color:#28b76b;border-color:#28b76b}.btn-primary:not(:disabled):not(.disabled):active,.btn-primary:not(:disabled):not(.disabled).active,.show>.btn-primary.dropdown-toggle{color:#fff;background-color:#1f8d53;border-color:#1d834c}.btn-primary:not(:disabled):not(.disabled):active:focus,.btn-primary:not(:disabled):not(.disabled).active:focus,.show>.btn-primary.dropdown-toggle:focus{box-shadow:0 0 0 .2rem rgba(72,194,129,0.5)}
```

所以若套用了 Bootstrap 框架, 只要替換相關符合 Bootstrap 的 CSS, JS 檔案, 即可馬上更換新的 UI.

## bootstrap-flask

[Bootstrap-Flask](<https://bootstrap-flask.readthedocs.io/en/latest/>) 是從[Flask-Bootstrap](<https://pythonhosted.org/Flask-Bootstrap/>)繼承過來的, 因為 Flask-Bootstrap 只有支持 Bootstrap 3, 並不支持 Bootstrap 4. 而 Bootstrap-Falsk 支持到 Bootstrap 4. 所以這裡採用 Bootstrap-Flask.

**為什麼要使用 Bootstrap-Flask?**

其實不一定要用, 可以直接在 template 中的相關 html page, 自己依照 Bootstrap 來編寫組合頁面, 但是 Bootstrap-Flask 根據常用的幾種場景歸納出幾個 [Marcos](<https://bootstrap-flask.readthedocs.io/en/latest/basic.html#macros>), 讓你在編寫 template html 可以少掉很多的工. 主要是分成四大類:

- form
- navbar
- pagination
- utils

但 utils 就不推薦用了.

### 初始化 bootstrap-flask

```python __init__.py
# ...
from flask_bootstrap import Bootstrap

app = Flask(__name__)
# ...
bootstrap = Bootstrap(app)
```

這裡要注意的是 `from flask_bootstrap import Bootstrap`, 雖然是使用 Bootstrap-Flask ,但是引用 package 時還是 `flask_bootstrap` 而不是 `bootstrap_flask`.

### load css & JS

程式中載入了 Bootstrap, 其實他所提供的 function 是回傳出 相對應的 html 語句. 將這些語句整合到 template html page 中, 才會呈現出 Bootstrap 的介面.

首先要在 `<head>` 段落中透過放入 `{{ bootstrap.load_css(version='4.3.1') }}` 在經由 jinja2 轉換得到 `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" type="text/css">`, 如此該 html 頁面就載入了 Bootstrap 4.3.1 版的 css.

因為 Bootstrap css 內部也用到 Jquery & popper 這兩個 js packages ,所以也要在該 html 頁面的 `<body>` 段落最後面同時載入. 透過 `{{ bootstrap.load_js(version='4.3.1', jquery_version='3.3.1', popper_version='1.14.0', with_jquery=True, with_popper=True) }}`, 最後會轉換成 `<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js"></script>` , `<script src="https://cdn.jsdelivr.net/npm/jquery@3.3.1/dist/jquery.min.js"></script>` , 以及 `<script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.0/dist/umd/popper.min.js"></script>`.

由上面可知 Bootstrap-Flask 預設是透過網路上的 CDN 來獲取這些資源, 其實可以透過 <https://www.bootcdn.cn/twitter-bootstrap/> （國內) <https://www.bootstrapcdn.com/> (國外) 來獲取. 不過若使用 Bootstrap-Flask 來載入, 則依照上面的方式是無法更換的.

#### local bootstrap css & JS

讚安裝好 Bootstrap-Flask 後, 其實在 local 也已經放置了 Bootstrap 相關的 css & JS, 可以在 `pythonversion/lib/python3.7/site-packages/flask_bootstrap/static/` 找到 css & JS 兩個目錄, 但是這裡面的版本不是最新的, 是 4.1.

若想使用 local 的版本, 必須在 config.py 中放入如下設定

```python config.py
class Config(object):
    # ...
    BOOTSTRAP_SERVE_LOCAL = True
```

如此就可以載入 local css & JS.

### 美化 Navbar

雖然 Bootstrap-Flask 對於 Navbar 提供了一個 marcro - `render_nav_item()`, 但是大部分的 navbar UI 還是要參考 [Bootstrap 官網](<https://getbootstrap.com/docs/4.3/components/navbar/#supported-content>).

#### 增加 Navbar 中的 logo 及標題

```html base.html
    <nav class="navbar navbar-expand-md sticky-top navbar-dark bg-primary">
        <!-- ... -->
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <img src="{{ url_for('static', filename='frog.svg') }}" width="30" height="30" alt="">
                MicroBlog
            </a>
```

主要是 `navbar-brand` 這個 tag, 若要增加 logo 則是在內部加上 `<img>` 即可

#### url_for()

要注意的是, template html page 中所有的 URL 必須透過 `{{ url_for() }}` 來填寫, 若是直接填入 URL 會有可能導致渲染時產生錯誤的 URL, 因為 Flask 最後都會透過 Jinja2 來轉換成最後的 html.

#### nav-item

利用 `render_nav_item(endpoint, text, badge='', use_li=False)` 來增加 nav-item. 

- endpoint: 填入相對應的 route, 就是在 `routes.py` 中所指的 route.
- text: 呈現出來的名稱.
- badge: 小提示的文字.
- use_li: 最後呈現的 html 是否以 `<li>` 呈現.

假若 endpoint 對應的 route 是像 `/user/<username>`, 則可以直接加上新的參數 `username='brad'`, `{{ render_nav_item('user', 'Profile', use_li=True, username=current_user.username) }}`.

```html base.html
<!-- ... -->
    <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mr-auto">
            {{ render_nav_item('index', 'Home', use_li=True) }}
            {{ render_nav_item('explore', 'Explore', use_li=True) }}
            {% if not current_user.is_anonymous %}
                {{ render_nav_item('user', 'Profile', use_li=True, username=current_user.username) }}
                {{ render_nav_item('create_post', 'New Post', use_li=True) }}
            {% endif %}
        </ul>
    </div>

```

### 美化 form

我認為 Bootstrap-Flask 對 Flask-WTF 的整合很不錯, 只要是繼承 `FlaskForm`, 只要對 form 中的每一個 Field 填好相關的設定, 在 template form html page 中只要透過 `{{ render_form(form, novalidate=True, button_map={'submit':'primary'}) }}`, 最後就可以轉換成相對應的 bootstrap html form. <https://getbootstrap.com/docs/4.3/components/forms/>

```html register.html
{% from 'bootstrap/form.html' import render_form %}
{% extends "base_t.html" %}

{% block content %}
    <div class="py-3 text-center">
        <h2>{{ title }}</h2>
    </div>
    <div class="row">
        <div class="col-md-12 col-lg-12 col-xl-12 col-sm-12">
            {{ render_form(form, novalidate=True, button_map={'submit':'primary'}) }}
        </div>
    </div>
{% endblock %}
```

其實本案列中, register.html, reset_password_request.html, reset_password.html, edit_profile.html 這些檔案, 其內容都是一樣, 也就是透過 Bootstrap-Flask 加上 Flask-WTF 來簡化.

在 forms.py 中可以看到每一個 form 中的每一個 field 被仔細地描述內容.

### 美化 Pagination

透過 `render_pagination()`, [Bootstrap Pagination](<https://getbootstrap.com/docs/4.3/components/pagination/>)所要使用的語句

```html
<nav aria-label="Page navigation example">
  <ul class="pagination justify-content-center">
    <li class="page-item disabled">
      <a class="page-link" href="#" tabindex="-1" aria-disabled="true">Previous</a>
    </li>
    <li class="page-item"><a class="page-link" href="#">1</a></li>
    <li class="page-item"><a class="page-link" href="#">2</a></li>
    <li class="page-item"><a class="page-link" href="#">3</a></li>
    <li class="page-item">
      <a class="page-link" href="#">Next</a>
    </li>
  </ul>
</nav>
```

都只要利用 `render_pagination()`, <https://github.com/greyli/bootstrap-flask/blob/master/flask_bootstrap/templates/bootstrap/pagination.html>, 其實只要傳入第一個參數 - flask_sqlalchemy.Pagination object - 就可以幫忙完整渲染出 pagination.

首先獲得 `flask_sqlalchemy.Pagination` object, 透過 `paginate()` 就可獲得

```python routes.py
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    return render_template('user.html',
                           user=user,
                           pagination=posts,
                           posts=posts.items)

```

填入 `render_pagination()`

```html user.html
<!-- ... -->
    {% if posts %}
    {% include '_post.html' %}
    {{ render_pagination(pagination, align='center') }}
    {% endif %}
<!-- ... -->
```

## 如何快速更換 Bootstrap 的 UI

以上的方式就可將整個網頁換成一個標準 Bootstrap 外形.

網路上有各種依照 Bootstrap 框架完成的各類 css, 要錢的或免費的, 例如 <https://startbootstrap.com/themes/>, <https://bootstrapmade.com/>, 其實還有很多.

### 案例說明

<https://themes.3rdwavemedia.com/demo/coderdocs/>, 我要將原本的標準 bootstrap style 換成鏈結中的樣式, 從下載中的資料將整個 `assets` 目錄拷貝一份到本專案的 `/app/static` 目錄底下.

新增一個 `base_t.html`, 繼承 `base.html`, 將原本引用 `base.html` 改成 `base_t.html`.

```html base_t.html
{% extends "base.html" %}

{% block styles %}
<!-- Google Font -->
<link href="https://fonts.googleapis.com/css?family=Poppins:300,400,500,600,700&display=swap" rel="stylesheet">
    
<!-- FontAwesome JS-->
<script defer src="{{ url_for('static', filename='assets/fontawesome/js/all.min.js') }}"></script>

<!-- Theme CSS -->
<link id="theme-style" rel="stylesheet" href="{{ url_for('static', filename='assets/css/theme.css') }}">
{% endblock %}

{% block scripts %}
    <script src="{{ url_for('static', filename='assets/plugins/jquery-3.4.1.min.js') }}"></script>
    <script src="{{ url_for('static', filename='assets/plugins/popper.min.js') }}"></script>
    <script src="{{ url_for('static', filename='assets/plugins/bootstrap/js/bootstrap.min.js' )}}"></script>
{% endblock %}
```

`base_t.html` 的內容就參考剛剛下載目錄中的 `index.html`, 看他載入哪些 css and js files, 我們就相對應的更換成這些檔案.

注意的是 href\src 的使用, `{{ url_for('static', filename='assets/fontawesome/js/all.min.js') }}`

如此就可以快速更換 style.
