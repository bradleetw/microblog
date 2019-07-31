# [CH8: Followers](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers>)

## 根據 粉絲架構 重新定義資料庫結構

所謂的粉絲架構主要是兩個角色 - 被關注者 和 粉絲, 而這兩個角色在我們前面的設計中都是 `User` model. 一個 User 可以關注很多的使用者(被關注者), 同時間也可以被很多的使用者關注(粉絲). 但是在 Relational Database 的 Table 中並沒有 list 的型態可以使用, 所以要如何在 `User` model 中記錄一個使用者關注的對象及粉絲呢？

使用者和被關注者的 link, 使用者和粉絲的 link, 都是一種關係的呈現.

### 一對多的關係

回顧[第四章](</04_database.md>)中所設計的帖子功能, 我們設計了兩個實體(entities) - users and posts. 一個使用者可以發很多的帖子, 而一個帖子只會由一位使用者發出. 一個 1 對 多 的關係.

在代碼中可以很容易看出哪一個實體是屬於 `多` 的一方, 只要透過 `db.ForeignKey()` 來指定, 則該實體及為 `多` 的一方.

一張帖子(post)可以依據 `user_id` 欄位來找到該帖子的作者資料, 但要如何找尋某個使用者的所有帖子? 只要對 `post table` 執行查詢 `user_id` 就可以很快找到.

### 多對多的關係

一個多對多的關係就像是兩個 `一對多關係` 合起來一樣的關係. 但卻無法像前面一樣, 只要再 `多` 的一方的實體中加上 `ForeignKey` 就可以, 因為在兩個實體中的加上 `ForeignKey` 是無法達成多對多的關係.

必須利用第三個 auxiliary table, `association table`, 來紀錄關聯, 而一筆關聯紀錄, 就紀錄著 2 個實體的 `ForeignKey`.

## 粉絲架構 的資料庫

粉絲和被關注者就是一種多對多的關係, 特別的是 粉絲和關注者 都是 `User` 實體. 需要定義另一個 `association table` 來記錄關係, 該 table 中就只有兩個 `ForeignKey` 的欄位, 分別紀錄被關注者和粉絲的 `user_id`.

### 資料庫的實現

#### 建立 association table

- `follower_id` 指的是 **粉絲**.
- `followed_id` 則是 **被關注者**.

要注意 `er` and `ed` 的差別, 很容易搞錯.

```python models.py
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey("user.id")),
    db.Column('followed_id', db.Integer, db.ForeignKey("user.id")))
```

因為該 `association table` 是輔助用, 並沒有額外紀錄其他的資料, 除了 `ForeignKey`, 所以就沒有採用 `User` & `Post` 一樣的方式繼承 `db.Model`, 而是直接建立 `db.Table()`, 並用 followers 來命名.

~~我們利用 User.followers 來記錄 `followers` 這個 association table, 會讓我誤會該語意描述著每一個 User 都有自己獨立的 `followers` table, 所以該系統會存在ㄧ個 User table, 一個 Post table, 以及多個 followers table (有多少個 User 就會有多少個 followers table), 但這是錯的.~~

系統中只會有 3 個 table, User, Post, and followers 這三個.

#### 建立多對多關係連結

如前面所說被關注者和粉絲都是 `User` 實體, 為了方便描述, 我們這裡定義 `左邊 User` 實體是**粉絲**, `右邊 User` 實體是**被關注者**, 再來我們在 `左邊 User`(粉絲) 中利用 `db.relationship` function 來記錄所關注的 User(也就是這關係是描述著粉絲關注著被關注者), 將這樣的關係定為 followed. 而我們站在 `右邊 User`(被關注者) 的方面來看這個關係, 我們定義為 followers.

``` python models.py
class User(UserMixin, db.Model):
    # ...
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
```

- 第一個參數放的是 `右邊 User` 的實體名稱, 剛好也是 `User`.
- 第二個參數 secondary: 傳入描述該關係的 association table, 這裡是 followers.
- 第三個參數 primaryjoin: 因為是`粉絲關注著被關注者`關係, primary 在這裡指的是`粉絲`, 所以這個參數要傳入的為 - 該 User (id) 是否為 association table 中的 `followers.c.follower_id` (粉絲id).
- 第四個參數 secondaryjoin: secondary 再者裡指的是 `被關注者`. 所以這個參數要傳入的為 - 該 User (id) 是否為 association table 中的 `followers.c.followed_id` (被關注者id).
- 第五個參數 backref: 描述 `被關注者` 也就是右邊的 User, 該如何訪問 association table, 也就是右邊的 User(被關注者)如何看待這層關係, 就是被關注者被粉絲關注的關係, 這裡我們已經定義為 `followers`, 方式為 `dynamic`.
- 第六個參數 lazy: 描述 `粉絲` 也就是左邊的 User, 該如何訪問 association table. 直接用 'dynamic' 表示採用的查詢執行模式是不會立即執行, 直到被調用.

## 關注/取消關注 的功能

SQLAlchemy ORM 將 followed 關係抽象成 `list`, 所以只要透過 `user1.followed.append(user2)` & `user1.followed.remove(user2)` 就可以讓 user1 關注/取消關注 user2.

```python models.py
class User(UserMixin, db.Model):
    # ...
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
```

除了在 User 中增加 `follow()` & `unfollow()` 外, 多新增 `is_following()` 來判斷使否關注過另一個使用者.

## 將粉絲機制整合到應用中

在 Flask 應用中增加兩個功能: `follow` & `unfollow`. 直接利用在 models.py 中的 User.follow(user) & User.unfollow(user) 實現. 要特別注意的是根據 username 來獲取 User 實體時要做的錯誤處理.

```python routes.py
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}')
    return redirect(url_for('user', username=username))
```

```python routes.py
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}')
    return redirect(url_for('user', username=username))
```

功能完善後, 接著調整 User Profile Page:

1. 呈現粉絲人數的數量, 及關注的數量.

2. 增加給使用者點擊 follow/unfollow 的 item.

```html user.html
        ...
        <p>{{ user.followers.count() }} followers, {{ user.followed.count() }} following.</p>

        {% if user == current_user %}
            <p><a href="{{ url_for('edit_profile') }}">Edit your profile</a></p>
        {% elif not current_user.is_following(user) %}
            <p><a href="{{ url_for('follow', username=user.username) }}">Follow</a></p>
        {% else %}
            <p><a href="{{ url_for('unfollow', username=user.username) }}">Unfollow</a></p>
        {% endif %}
        ...
```

## 獲取關注用戶的動態

增加粉絲和被關注者關係的功能, 還不夠有趣. 做到呈現所感興趣的使用者的動態, 這個功能更有趣.

而要如何呈現這些動態就是這段要探討的主題 - 要如何撈取(query) Post table 這個資料表?

首先可以透過 `user.followed.all()` 獲取所有我們關注的名單, 然後再來獲取所有被關注者的 Post. 假設關注了 1000 個使用者, 則需要對資料庫做 1000 的獲取 post 的動作以獲得所有感興趣的 posts. 再將這所有的 posts 合併排序(存在 memory中), 假若已完成`分頁`功能, 則接著再分段呈現出來. 這些動作若沒有透過 relational database 所提供的功能, 則非常沒有效率.

主要是透過 `join()`, `filter()`, `order_by()` 這三個 function 來做到以上的事:

- **join()**: 將資料庫中的表格關聯起來

- **filter()**: 將符合條件的資料篩選出來

- **order_by()**: 照時間順序排序

### 聯合查詢

我們要找出我們有關注的使用者的 Posts, 所以須先將 Post table 和 association table - followers 做連結, 所以條件是 `followers.followed_id == Post.user_id`:

```python 
followed = Post.query.join(followers, (followers.followed_id == Post.user_id))
```

所得到的 `followed` 就是依照 `Post.user_id` & `followers.followed_id` 必須相等的條件連結出來的大表格.

如果今天是要找粉絲的動態, 就要參考如下改法, 將 `followers.followed_id` 換成 `followers.follower_id`:

```python
followed = Post.query.join(followers, (followers.follower_id == Post.user_id))
```

### filter

要呈現該登入使用者所有關注的所有動態, 也就是從上面 join 後的大表中, 查找粉絲欄位(followers.follower_id)是該登入使用者的 id (self.id):

```python
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.followed_id == Post.user_id)).filter(
                followers.follower_id == self.id)
```

### 排序

由於我們是要依據所有 Posts 被建立的時間來呈現, 所以要挑選 `Post.timestamp` 來當作排序的 index. 

```python
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.followed_id == Post.user_id)).filter(
                followers.follower_id == self.id).order_by(
                    Post.timestamp.desc()
                )
```

### 將所有的關注者及自身的動態呈現出來

前面只有將被關注者的動態呈現出來, 但看不到使用者本身的動態(因為使用者自己無法關注自己), 為了也一起呈現使用者本身的動態資料, 所以必須額外查找使用者本身的 Post.

```python
own = Post.query.filter_by(user_id=self.id)
```

找到後再和前面所找到資料透過 `union()` 合併.

```python
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
```

## Unit Testing

