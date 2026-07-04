# 项目结构说明

这份文档只说明当前主流程。`examples/` 和 `docs/langchain.md` 是说明或历史材料，不参与微信机器人运行。

## 启动流程

```text
app.py
  -> 设置项目根目录和微信域名代理绕过
  -> 检查 config/config.yaml、logs/、data/
  -> wxbot.main()
      -> WxBot()
      -> itchat.auto_login()
      -> itchat.run()
```

## 主流程文件

- `app.py`
  - 程序入口。
  - 负责启动前环境准备，不处理微信消息业务。

- `wxbot.py`
  - 微信消息入口。
  - 负责注册 itchat 回调、判断私聊/群聊、调用业务服务、发送消息。
  - 不应该继续塞复杂业务逻辑，后续新增能力优先放到 `services/` 或 `plugins/`。

- `utils/instruct.py`
  - 普通命令路由。
  - 识别 `#help`、`帮助`、`#admin`、`/img`、`/url`。

- `admin/admin.py`
  - 管理员命令解析。
  - 把 `#admin $role xxx` 解析成结构化的 `AdminCommand`。
  - 只负责解析，不直接修改机器人状态。

## 服务层

- `services/chat_service.py`
  - GPT 聊天主服务。
  - 管理群聊/私聊角色、模型、OpenAI key 轮询、上下文记忆。

- `services/admin_service.py`
  - 管理员命令执行。
  - 负责角色、模型、群聊/好友白名单的修改。

- `services/runtime_state.py`
  - 运行态持久化。
  - 保存管理员运行时修改的角色、模型、群聊/好友白名单。
  - 文件位置：`data/runtime_state.json`。

## OpenAI 和绘图

- `plugins/openai/role.py`
  - OpenAI/LangChain 客户端封装。
  - `ChatGpt`：聊天回复和记忆摘要压缩。
  - `DrawingGenerator`：OpenAI 图片生成。

- `plugins/sd.py`
  - Stable Diffusion 绘图接口。

## 工具层

- `config/config.py`
  - 读取并校验 `config/config.yaml`。
  - 内部用 dataclass 表示配置。
  - 仍保留旧属性名，比如 `config.openai_api_key`、`config.GroupChatList`。

- `config/log.py`
  - 日志配置。
  - 使用滚动日志，单个文件 5MB，保留 3 份备份。

- `config/paths.py`
  - 项目路径统一定义。
  - 避免从不同目录启动时路径错乱。

- `utils/memory_store.py`
  - 每个好友/群成员独立记忆。
  - 记忆分为 `facts`、`summary`、`recent_messages` 三层。
  - 保存目录：`data/memory/`。

- `utils/message.py`
  - 把 GPT 回复按句子拆成多条微信消息。
  - 遇到代码块会保留整段，避免把代码拆坏。

- `utils/generateList.py`
  - OpenAI key 轮询。

- `utils/util.py`
  - 目前仍是杂项工具，后续建议继续拆。

## 数据和配置

- `config/config.yaml`
  - 本地真实配置，包含 key，不提交。

- `config/config copy.yaml`
  - 配置模板。

- `data/runtime_state.json`
  - 管理员命令运行时改动。
  - 重启后仍生效。

- `data/memory/`
  - 每个好友/群成员的聊天记忆。
  - `facts` 保存稳定事实。
  - `summary` 保存旧对话摘要。
  - `recent_messages` 保存最近原文消息。

- `logs/app.log`
  - 运行日志。

## 消息处理流程

### 私聊

```text
微信私聊消息
  -> wxbot.handle_friend_chat()
  -> 检查是否自己发的消息
  -> 检查好友白名单
  -> Instruct.question()
      -> #help / #admin / /img / 普通聊天
  -> 普通聊天进入 ChatService.reply()
  -> split_chat_reply()
  -> 分多条发回微信
```

### 群聊

```text
微信群消息
  -> wxbot.handle_group_chat()
  -> 必须 @ 机器人
  -> 检查群白名单
  -> 清理 @ 文本
  -> Instruct.question()
  -> 普通聊天按 group_id + member_id 生成独立 session
  -> ChatService.reply()
  -> 第一条 @ 发起人，后续自然拆句发送
```

## 管理员命令

```text
#admin
#admin $role 角色提示词
#admin $model 模型名
#admin $addFriendChat 好友备注名
#admin $delFriendChat 好友备注名
#admin $addGroupChat 群聊名称
#admin $delGroupChat 群聊名称
```

注意：

- 管理员权限目前仍按备注名/昵称判断。
- 好友/群白名单目前也按备注名/群名判断。
- 这是后续最值得继续优化的点，因为改名会导致匹配失效。
