# env

python = 3.10

create environment from environment.yml using anaconda

# todo

- 页数超过限制，没做，估计可以不做了，因为很难超过限制
- 请求超时、请求重试，没做，都是国内网址应该很难出问题，这个很难做
- 计时装饰器，没做
- 日志，没做，可能不需要
- config文件，没做，可能不需要，config里面也就塞个代理什么的
- 数据库service，没做

注：

- 页面处理逻辑是先通过re的match，然后再json化，这个过程出问题的可能性很多：1、请求超时、请求异常、代理异常；2、状态码异常；3、无法match；4、json化失败；5、json化后解析为xpath无法找到li标签
- 具体li的处理，部分我是允许返回空的，但是一些字段是我强制要求要返回的，比如标题，但是不保证处理过程中就有攻略没有标题；无法保证获取到的li标签就是有效的
- 筛选功能一切基于返回的li标签（因为我是按页码非并发地顺序扫描）自己已经基于时间倒序排序
- 尚不知晓游民星空是否含有ip封禁功能

08-17
- 支持多页处理

08-16
- 移动下载模块到middleware类。
- 加入ID检测机制，重复内容不再获取。

08-15
- 保存一份原始带标签的数据json，保存一份经过处理的干净文本txt

08-14
- 将文本处理方法移动到text_processor类
- 在本地化之前检查content长度，过短的不做本地化。

08-11
- 添加多tag处理逻辑，正确处理p, div与ul等标签里的内容

08-07

1. [x] 模式匹配基于p标签，如果p标签属性不够满足模式匹配全部条件，需要细化标签
2. [x] 需要text后处理
3. [ ] 目前没有异常处理逻辑
4. [x] 目前不能处理多页
5. [ ] 目前不能处理视频
6. [ ] 无监管自动更新
    - 定时触发爬取函数，所有数据存放到当天文件夹内
    - 设置一个函数从前端选择当天爬取的所有文件，多选，获得标题的列表
    - 将列表内标题的文件通过更新函数，数据库入库