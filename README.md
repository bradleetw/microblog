# Notes

## [Chapter 1](<https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world>)

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


