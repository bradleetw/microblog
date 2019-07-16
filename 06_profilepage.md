# CH6: [Profile Page and Avatars](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vi-profile-page-and-avatars>)

## User Profile Page

### 傳遞參數

在 `@app.route()` 中變數由 `<` & `>` 包起來傳入 view function , 也可以指定變數型態, eg. `@app.route('/user/<int:id>')`.

```python
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)
```

### return 404 error directly if not found data form database

透過 `first_or_404()` 直接獲得資料或者直接回傳 404 error(表示找不到).

產生一個簡單的頁面來呈現 user profile:

```html user.html
{% extends "base.html" %}

{% block content %}
    <h1>User: {{ user.username }}</h1>
    <hr>
    {% for post in posts %}
    <p>
    {{ post.author.username }} says: <b>{{ post.body }}</b>
    </p>
    {% endfor %}
{% endblock %}
```

增加一入口在 navigation bar:

```html base.html
    <div>
      Microblog:
      <a href="{{ url_for('index') }}">Home</a>
      {% if current_user.is_anonymous %}
      <a href="{{ url_for('login') }}">Login</a>
      {% else %}
      <a href="{{ url_for('user', username=current_user.username) }}">Profile</a>
      <a href="{{ url_for('logout') }}">Logout</a>
      {% endif %}
    </div>
```

`<a href="{{ url_for('user', username=current_user.username) }}">Profile</a>`, 透過 url_for() 傳入變數資料的方式.

### Avatars

可以將大頭貼放在 `https://www.gravatar.com/avatar/\<hash\>` 這個網站, \<hash\> 裏頭直接是 email address 的 MD5. 他也提供給沒有在 gravatar 註冊的使用者一些隨機圖片, `https://www.gravatar.com/avatar/\<hash\>?d=identicon&s=128`, 一樣在 \<hash\> 裡換成 email address 的 MD5 value.

gravatar 除了有 `identicon`, 還可以換成 `mp`, `monsterid`, `wavatar`, `retro`, and `robohash` 這些不同類型的圖.

gravatar 提供的尺寸大小, 1 px 到 2048 px.

給 User 增加一個方法可以直接回傳 gravatar URL.

```python models.py
from hashlib import md5
# ...

class User(UserMixin, db.Model):
    # ...
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
```

將圖案整合到 user profile page:

```html user.html
{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
    <p>
    {{ post.author.username }} says: <b>{{ post.body }}</b>
    </p>
    {% endfor %}
{% endblock %}
```

### 將會共用的 template html page 分離出來

接下來會在 index.html 的頁面中也渲染出 每一個 post, 所以將相關的分離出來到 `_post.html`, 然後利用 `jinja2` 的 `{% include '_post.html' %}` 來引入子頁面.

```html _post.html
    <table>
        <tr valign="top">
            <td><img src="{{ post.author.avatar(36) }}"></td>
            <td>{{ post.author.username }} says:<br>{{ post.body }}</td>
        </tr>
    </table>
```

```html user.html
{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
        {% include '_post.html' %}
    {% endfor %}
{% endblock %}
```

### 增加資料庫 User table 的欄位

對每一個 user profile 增加一個 `about me` 的自我描述欄位, 以及一個紀錄該使用者最近一次登入的時間.

```python models.py
class User(UserMixin, db.Model):
    # ...
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
```

因為資料庫的欄位結構變更, 所以要進行一次 [migration](</04_database.md#How-to-maintain-databse-migration>) 的動作.

```cmd
flask db migrate -m "new fields in user model"
```

`-m` 就是記錄這次 migrate 要寫下的註釋.

接著執行 upgrade

```cmd
flask db upgrade
```

然後在 user profile page 裡再加上 `about me` & `last seen` 這兩個欄位的資料.

```html user.html
{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td>
                <h1>User: {{ user.username }}</h1>
                {% if user.about_me %}<p>{{ user.about_me }}</p>{% endif %}
                {% if user.last_seen %}<p>Last seen on: {{ user.last_seen }}</p>{% endif %}
            </td>
        </tr>
    </table>
    ...
{% endblock %}
```

### 記錄使用者最新一次拜訪的時間

可以在每一個頁面都執行紀錄被 request 的當下時間功能, 但是這樣很麻煩, 因為會需要在每一個新的頁面功能建立時, 都要額外做這功能. 可以透過 Flask 提供的 `@app.before_request` 來在每一個 request function 之前執行同樣的事.

```python routes.py
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
```

### 編輯 user profile

建立一個讓使用者修改姓名, 自我描述的 form.

```python forms.py
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

# ...

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
```

```html edit_profile.h
{% extends "base.html" %}

{% block content %}
    <h1>Edit Profile</h1>
    <form action="" method="post">
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}<br>
            {% for error in form.username.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.about_me.label }}<br>
            {{ form.about_me(cols=50, rows=4) }}<br>
            {% for error in form.about_me.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

```python routes.py
from app.forms import EditProfileForm

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
```

在以上的代碼片段中, 會突然認為 `current_user.username` & `form.username` 是相同的類, 事實上:

1. **current_user.username**: 這是 models.py 中 User.username (current_user 是一個 User 的 proxy), 是一個單純字符串

2. **form.username**: forms.py 中的 EditProfileForm.username, 是一個 wtforms.StringField 物件, 所以要獲得裡面的資料就必須使用 form.username.data
