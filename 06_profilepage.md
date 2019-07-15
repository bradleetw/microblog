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

```python
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

```html
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
