# 使用方法

## 运行环境

在`python3.7.4`中通过测试，其他环境未测试

python最低要求为`python3.6`

## 主程序

导入yobot并调用

```python
import yobot
bot = yobot.Yobot()
reply = bot.proc(context)
```

其中：
`reply`是一个`str`；
`context`是一个`dict`，其结构为

```python
context = {
    "group_id": 12345, # 聊天编号（QQ群号）
    "raw_message": "你好", # 消息内容
    "sender": {
        "user_id": 456, # 用户编号（QQ号）
        "nickname": "nickname", # 用户昵称
        "role": "admin" # 用户身份
    }
}
```

主文件`main.py`是利用`aiocqhttp`的应用

## 增加功能

### 被动回复

在![custom.py](https://github.com/yuudi/yobot/tree/master/src/client/plugins/custom.py)文件中可以增加简单的功能

### 主动推送

#### RSS订阅

在![push_news.py](https://github.com/yuudi/yobot/tree/master/src/client/plugins/push_news.py)文件里可以添加RSS订阅源

在`self.rss`里添加订阅，格式如下

```python
"news_jp_official": # 订阅名称，在yobot_config.json文件中控制开关的名称相同
{
    "name": "日服官网", # 可读的名称
    "source": "https://priconne-redive.jp/news/feed/", # 订阅地址
    "pattern": "标题：{title}\n链接：{link}\n{summary}", # 转化为字符串的方法
    "last_id": None # 此项必须为 None
}
```

#### 爬虫

在![spider](https://github.com/yuudi/yobot/tree/master/src/client/plugins/spider)文件夹中可以添加爬虫

例子：![official_site_tw.py](https://github.com/yuudi/yobot/tree/master/src/client/plugins/spider/official_site_tw.py)

导入父类，创建一个子类

```python
from .base_spider import Base_spider, Item

class Spider_ostw(Base_spider):
    ...
```

编写属性

```python
    def __init__(self):
        super().__init__()
        self.url = "http://www.princessconnect.so-net.tw/news/" # 地址来源
        self.name = "台服官网" # 可读的名称
```

编写分析器

```python
    def get_items(self):
        soup = self.get_soup() # 获取BeautifulSoup对象
        if soup is None:
            return None
        return [
            Item(
                # 编号，整数或字符串，判断新闻是否相同的依据
                idx=dd.a["href"],

                # 内容，字符串，要发送的新闻
                content="{}\n{}".format(dd.text, urljoin(self.url, dd.a["href"]))
            )
            for dd in soup.find_all("dd")
        ]
```

加入订阅（在![__init__.py](https://github.com/yuudi/yobot/tree/master/src/client/plugins/spider/__init__.py)文件里）

```python
# import新编写的子类
from .official_site_tw import Spider_ostw

class Spiders:
    def __init__(self):
        self.spiders = {
            "news_tw_official": Spider_ostw()
            # 将新的订阅加入
            # 键：订阅名称，在yobot_config.json文件中控制开关的名称相同
            # 值：对象，由新编写的子类创建出的对象
        }
    ...
```
