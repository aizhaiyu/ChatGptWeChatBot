# ChatGptWeChatBot

#### 介绍
基于openai chatgpt的微信机器人，支持key轮询，openai绘图，sd绘图，私聊群聊，自定义角色等。

### 运行环境

平台：Windows/liunx

python版本`>=3.8.1<4.0`

#### 软件架构
本项目使用了itchat的库，以及langchain作为主要对接。
- admin
    - admin.py 管理员指令
- config
    - config copy.yaml 用户配置文件
    - config.py 读取配置文件
    - log.py 日志配置文件
- docs 文档加载
- img 图片绘画存放位置
- logs 日志
- lib 依赖包
- plugins 功能插件
- utils 常用功能
- wxbot.py 微信机器人主要实现

#### 安装教程

1. 安装python *>=3.8.1<4.0* 版本
2. 进入项目目录chatgptWxBot
3. 控制台安装需要的库
    `pip install -r requirements.txt`
4. 运行app.py文件

#### 使用说明

1. 先更改config/config copy.yaml文件名重命名为config.yaml
2. 打开config.yaml配置文件，将管理员微信名，openai key填写上即可
3. 群聊需艾特机器人 输入#help查看使用教程

#### 使用截图

<img src="img/%E4%BD%BF%E7%94%A8.jpg" width="200">
<img src="img/%E5%8A%9F%E8%83%BD.jpg" width="200">
<img src="img/%E7%AE%A1%E7%90%86.jpg" width="200">

#### 加入群聊
加入群聊的好处：及时通知危险资讯，更新内容，解决问题

![img](img/ai.png)

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


