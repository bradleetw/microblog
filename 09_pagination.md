# [CH9: Pagination](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ix-pagination>)

## 完善 Blog feature

在這個章節前半段中, 提供讓使用者發布訊息的功能, 呈現相關的 Posts 在首頁, 讓使用者更容易關注博主. 而這些功能我在第八章已經依照自己的需求完成.

在這段裡, 寫下一些我之前有誤解的部分.

### SQL Alchemy 的認知不足

跟著案例學習下來, 並沒有深入了解 [SQL Alchemy](<https://docs.sqlalchemy.org/en/13/core/tutorial.html>) & [flask-sqlalchemy](<https://flask-sqlalchemy.palletsprojects.com/en/2.x/>), 就會有很多的誤會.

#### 1 對多的關係

以下的方式定義了兩個實體的一對多關係. 透過 [db.relationship()](<https://docs.sqlalchemy.org/en/13/orm/relationship_api.html#sqlalchemy.orm.relationship>) 在 **1** 的這個實體中定義和另一個實體(第一個參數填入另一個實體的名稱)的關係, 並定義在 **多** 的那個實體中如何看待 **1** 這個實體(第二個參數 backref), 以及定義該利用何種方式將關聯的實體[**載入**](<https://docs.sqlalchemy.org/en/13/orm/loading_relationships.html>), 這裡是案例大多使用 [*dynamic**](<https://docs.sqlalchemy.org/en/13/orm/collections.html#dynamic-relationship>).

而在 **多** 的實體, 則必須加入一個放入 **ForeignKey** 的欄位, 紀錄屬於某一個的 **id**.

```python models.py
class User(UserMixin, db.Model):
    # ...
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # ...

class Post(db.Model):
    # ...
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
```

以上是定義的方法. 但使用上卻不清楚, 直到這個章節.

#### example 1

這個案例的目的是要將某一個 User 的所有 Post 做分頁的功能, 我原本是打算透過 `filter_by()` 將 User 的 primary key 傳入後, 撈出所有的 Post. 這是可行的. 但是已經前一行已經利用 `filter_by()` 將相對應的 User 實體撈出, 沒必要再做一次 `filter_by()`, 可以直接透過 User.posts 就是該 user 的所有 Post.

```python original
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
```
  
直接利用 User 的 posts 這個屬性.

```python new
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
```

#### example 2

另一個案例是善用 backref 所定義的名稱. 在產生一個新的 Post 時除了傳入 `title` & `body` 外, 也要傳入 **ForeignKey** - `user_id`, 但其實可以透過 **author** 直接傳入 User - `current_user`. 如此語意會更清楚.

```python original
        post = Post(title=form.title.data, body=form.body.data, user_id=current_user.id)
```

```python new
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
```

## 分頁

對於有非常多筆的資料頁面, 一次將所有的資料呈現出來是在體驗上以及實作上都是較不好的的設計. 對體驗上而言, 一直滾動頁面讓是使用者有閱讀上的恐慌, 不知何時才可結束, 如果資料有上千上萬筆. 而對實作上而言, 要一次要將多筆的資料同時放入 memory , 對於有限的 memory 空間是非常危險(將“無限”的資料, 放入“有限”的空間). 所以分頁功能就非常必要.

透過 flask-sqlalchemy 提供的 [paginate](<https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#flask_sqlalchemy.BaseQuery.paginate>) 來完成相關的動作.

透過 BaseQuery.paginate() 獲取 [Pagination](<https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/#flask_sqlalchemy.Pagination>) 物件. 列如:

```command
>>> pObj = user.followed_posts().paginate(1, 20, False)
>>> pObj.items
```

- paginate 的第一個參數指的是第幾頁
- paginate 第二個參數指的是每頁會有幾筆資料
- paginate 第三個餐數指的不要對發生的錯誤(如傳入第一\二個參數是負數或小數)直接引起 404 response, 而是直接將 第一個參數及第二個參數改成 1 & 20.

執行完後, 直接回傳一個 Pagination 的物件. 可以透過該物件的一些屬性來做頁面的呈現

- Pagination.has_next: 是否有下一頁
- Pagination.has_prev: 是否有前一頁
- Pagination.next_num: 下一頁的頁數
- Pagination.prev_num: 前一頁的頁數
- Pagination.items: 當前頁面的所有資料

### 透過應用 URL 的查詢字符串來告知第幾頁

```python routes.py
# ...
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Home Page', posts=posts.items, next_url=next_url, prev_url=prev_url)
```

因為是透過查詢字符串, 所以利用 `request.args.get('page', 1, type=int)` 來獲得要呈現第幾頁的數字, 若沒有傳入, 則預設是 1 .

透過 `Pagination.has_next` & `Pagination.next_num` 來組合產生下一頁的 URL. 

在渲染的頁面中增加如下:

```html index.html
    {% if prev_url %}
    <a href="{{ prev_url }}">Newer Posts</a>
    {% endif %}
    {% if next_url %}
    <a href="{{ next_url }}">Older Posts</a>
    {% endif %}
```