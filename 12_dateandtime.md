# [CH12: Dates and times](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xii-dates-and-times>)

利用 moment.js 以及 flask-moment 來處理前端頁面的 date & time 資料呈現.

## 不同時區的問題

假設你的網站的使用者是來自四面八方, 他們的時區各自不同, 要處理 date & time 資料時使用 UTC 則是必要的. 但是在呈現的時候, 必須依據個別時區來處理, 這是非常麻煩.

所以後台使用各訂的 UTC date time, 由前台來處理不同地方的時區呈現.

## 使用 [moment.js](<https://momentjs.com/>) & [flask-moment](<https://github.com/miguelgrinberg/Flask-Moment>)

利用 **moment.js** 可以讓前台很方便地處理日期和時間的呈現方式, 再透過 **flask-moment** 的包裝, 就可以很方便的整合進來.

### 載入 flask-momnet

就像一般的 flask package 傳入 app 到 Moment.

```python __init__.py
# ...
from flask_moment import Moment

# ...
moment = Moment(app)
```

在模板中加上以下的代碼,

```html base.html
    <!-- ... -->
    {{ moment.include_jquery() }}
    {{ moment.include_moment() }}
    {{ moment.locale(auto_detect=True) }}
```

moment.include_jquery() 要不要加可以取決於模板中是否已有加上 jquery. 

moment.locale(auto_detect=True) 則是讓一些英文的顯示根據使用者的瀏覽器設定而呈現出適當的語系.

### 如何使用 moment

在沒有 moment 時可以透過以下的方式來呈現日期時間,

```html _post.html
    <!-- ... -->
    <small class="text-muted">
        {{ post.timestamp.strftime('%Y-%m-%d %H:%M') }}
    </small>
```

```html user.html
    <p>
        Last seen on: {{ user.last_seen.strftime('%Y-%m-%d %H:%M') }}
    </p>
```

但是利用 moment.js, 可以依據 <https://momentjs.com/> 的方式來設定, 例如要呈現距離現在多久以前可以用 `moment().fromNow()`:

```html _post.html
    <!-- ... -->
    <small class="text-muted">
        {{ moment(post.timestamp).fromNow() }}
    </small>
```

或是 `moment().format('LLL')` 等方法.

```html user.html
    <p>
        Last seen on: {{ moment(user.last_seen).format('LLL') }}
    </p>
```
