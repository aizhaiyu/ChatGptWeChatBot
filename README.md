# ChatGptWeChatBot

基于 itchat + OpenAI 的微信机器人。当前版本已经在原项目基础上做过结构整理，支持：

- 私聊 / 群聊回复
- OpenAI key 轮询
- OpenAI 绘图
- Stable Diffusion 绘图
- 管理员命令
- 每个好友 / 每个群成员独立上下文记忆
- 事实记忆 + 对话摘要双层长期记忆
- GPT 回复按句子拆成多条微信消息
- 管理员运行时配置持久化

详细结构说明见 [docs/architecture.md](docs/architecture.md)。

本地改动记录见 [docs/changelog.md](docs/changelog.md)。

## 环境

- Python：`>=3.8.1,<4.0`
- macOS / Linux / Windows 理论可用
- 当前本机推荐环境：

```bash
conda activate chatgpt-wechatbot
```

如果本机有多个 Python，建议使用明确解释器：

```bash
/opt/homebrew/Caskroom/miniconda/base/envs/chatgpt-wechatbot/bin/python app.py
```

## 安装

```bash
cd /Users/wolfman/Documents/code/python/ChatGptWeChatBot
python -m pip install -r requirements.txt
```

如果你开了本地代理，例如端口 `7892`：

```bash
HTTPS_PROXY=http://127.0.0.1:7892 HTTP_PROXY=http://127.0.0.1:7892 python -m pip install -r requirements.txt
```

## 配置

先复制模板：

```bash
cp "config/config copy.yaml" config/config.yaml
```

然后编辑：

```bash
config/config.yaml
```

重点配置：

```yaml
wx_bot:
  admin:
    - 你的微信备注名
  chat:
    isGroupChat: True
    isFriendChat: True
    GroupChatList:
    FriendChatList:
    GroupChatRole: 群聊默认角色提示词
    FriendChatRole: 私聊默认角色提示词

openai:
  model_name: gpt-4o-mini
  temperature: 0.9
  threshold: 3
  openai_api_base: https://你的接口地址/v1
  openai_api_key:
    - sk-xxx
  draw:
    - 画
    - 畫
    - draw

memory:
  enabled: true
  dir: data/memory
  recent_limit: 12
  compress_threshold: 16
```

说明：

- `GroupChatList` 为空表示全部群可用。
- `FriendChatList` 为空表示全部好友可用。
- `admin`、好友白名单、群白名单目前按备注名 / 昵称 / 群名匹配。
- 改名后可能失效，这是后续还需要优化的点。

## 运行

```bash
cd /Users/wolfman/Documents/code/python/ChatGptWeChatBot
conda activate chatgpt-wechatbot
python app.py
```

启动后扫码登录微信。

如果微信登录受代理影响，`app.py` 已经默认把微信相关域名加入 `NO_PROXY`。

## 命令

私聊：

```text
#help
帮助
#admin
```

群聊需要先 `@机器人`：

```text
@机器人 #help
@机器人 #admin
```

管理员命令：

```text
#admin
#admin $role 角色提示词
#admin $model 模型名
#admin $addFriendChat 好友备注名
#admin $delFriendChat 好友备注名
#admin $addGroupChat 群聊名称
#admin $delGroupChat 群聊名称
```

管理员命令修改会保存到：

```text
data/runtime_state.json
```

所以重启后仍然生效。

## 记忆

默认开启独立记忆。

保存位置：

```text
data/memory/
```

私聊按好友分开保存。

群聊按 `群 + 成员` 分开保存。

消息达到阈值后会自动整理成两层长期记忆：

- `facts`：稳定事实，例如姓名、偏好、关系、长期目标、重要要求。
- `summary`：旧对话摘要，用来理解之前聊过什么。

当前模型请求会同时带上：

- 角色提示词
- 稳定事实记忆
- 对话摘要
- 最近几条原文对话
- 当前问题

## 当前结构

```text
app.py                         启动入口
wxbot.py                       微信消息处理入口
admin/admin.py                 管理员命令解析
config/config.py               配置读取和校验
config/log.py                  日志配置
config/paths.py                项目路径
plugins/openai/role.py         OpenAI 聊天和绘图封装
plugins/sd.py                  SD 绘图
services/chat_service.py       GPT 聊天和记忆压缩服务
services/admin_service.py      管理员命令执行
services/runtime_state.py      运行态持久化
utils/instruct.py              普通命令解析
utils/memory_store.py          事实记忆、对话摘要、最近消息存储
utils/message.py               多句回复拆分
utils/generateList.py          key 轮询
utils/util.py                  杂项工具
```

## 已优化内容

- 更新 LangChain / OpenAI 新写法。
- 移除旧的 OpenAI demo 文件，避免误导入。
- 管理员命令改成结构化解析，不再用函数名字符串当协议。
- 新增 `services/` 服务层，减少 `wxbot.py` 业务混杂。
- 新增独立长期记忆：事实记忆 + 对话摘要 + 最近消息。
- 新增运行态持久化，管理员改动重启不丢。
- 配置读取改为 dataclass + 类型校验。
- 日志改为滚动日志。
- 回复按句子拆成多条微信消息，代码块不乱拆。
- 路径统一由 `config/paths.py` 管理。

## 还需要继续优化

- 管理员权限、好友白名单、群白名单还在按昵称 / 备注名匹配，不够稳定。
- `wxbot.py` 仍然偏胖，可以继续拆成微信适配层、绘图服务、回复发送服务。
- `utils/util.py` 还是杂项集合，后续应该继续拆。
- 还没有正式 `pytest` 测试目录。
- SD 绘图和 OpenAI 绘图错误处理还可以更细。

## 常见问题

### `ModuleNotFoundError: No module named ...`

先确认在正确环境：

```bash
conda activate chatgpt-wechatbot
python -m pip install -r requirements.txt
```

### pip SSL 报错

如果你开了 VPN，本地代理端口是 `7892`：

```bash
HTTPS_PROXY=http://127.0.0.1:7892 HTTP_PROXY=http://127.0.0.1:7892 python -m pip install -r requirements.txt
```

### 登录成功但收不到回复

检查：

- `isFriendChat` / `isGroupChat` 是否开启。
- 私聊好友是否在 `FriendChatList` 里。
- 群聊是否在 `GroupChatList` 里。
- 群聊是否真的 `@机器人`。
- 当前发消息的人是否是机器人自己。

## 截图

<img src="img/%E4%BD%BF%E7%94%A8.jpg" width="200">
<img src="img/%E5%8A%9F%E8%83%BD.jpg" width="200">
<img src="img/%E7%AE%A1%E7%90%86.jpg" width="200">
