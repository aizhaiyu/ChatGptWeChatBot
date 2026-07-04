# 变更说明

## 当前版本改动

### 环境和依赖

- 更新 LangChain 相关依赖：
  - `langchain`
  - `langchain-openai`
  - `openai`
- 主聊天链路从旧的 `LLMChain/OpenAI` 写法改为 `ChatOpenAI.invoke()`。
- 删除旧的未维护 OpenAI 示例文件：
  - `plugins/openai/chatgpt_plugin.py`
  - `plugins/openai/chroma.py`
  - `plugins/openai/fun.py`
- 历史示例统一放到 `examples/`。

### 启动和路径

- 新增 `config/paths.py` 统一项目路径。
- `app.py` 现在会：
  - 切换到项目根目录。
  - 设置微信域名不走代理，减少 VPN 影响微信登录。
  - 检查 `config/config.yaml`。
  - 创建 `logs/` 和 `data/`。

### 配置系统

- `config/config.py` 从直接读取字典改为结构化 dataclass 配置。
- 增加配置类型校验和默认值。
- 配置错误会更早报出，例如：
  - `openai_api_key` 为空。
  - `threshold` 小于 1。
  - 布尔值写成字符串。

### 日志

- `config/log.py` 改为滚动日志：
  - 单个日志最大 5MB。
  - 保留 3 个备份。

### 管理员功能

- `admin/admin.py` 不再返回函数名字符串。
- 管理员命令现在解析为：
  - `AdminCommand`
  - `AdminAction`
- `services/admin_service.py` 负责真正执行管理员命令。
- 管理员命令保持兼容：
  - `#admin`
  - `#admin $role ...`
  - `#admin $model ...`
  - `#admin $addFriendChat ...`
  - `#admin $delFriendChat ...`
  - `#admin $addGroupChat ...`
  - `#admin $delGroupChat ...`

### 运行态持久化

- 新增 `services/runtime_state.py`。
- 管理员命令改动会保存到 `data/runtime_state.json`：
  - 群聊白名单
  - 好友白名单
  - 群聊角色
  - 私聊角色
  - 群聊模型
  - 私聊模型
- 重启后继续生效。

### 聊天记忆

- 新增 `utils/memory_store.py`。
- 每个好友、每个群成员都有独立上下文。
- 记忆保存在 `data/memory/`。
- 达到阈值后会自动整理成两层长期记忆：
  - `facts`：稳定事实，例如姓名、偏好、关系、长期目标、重要要求。
  - `summary`：旧对话摘要。
- 最近对话原文仍保存在 `recent_messages`。

### 回复体验

- 新增 `utils/message.py`。
- GPT 回复会按中文句子拆成多条微信消息。
- 多条消息之间有短暂停顿，更接近真人聊天。
- 代码块不会被拆散。

### OpenAI 封装

- `plugins/openai/role.py` 更新为新版 LangChain 写法。
- `ChatGpt` 支持：
  - 系统角色提示词。
  - 长期记忆摘要。
  - 最近对话消息。
- `DrawingGenerator` 更新为新版 OpenAI 图片生成写法。

### 工具加固

- `utils/generateList.py`
  - 空 key 列表会提前报错。
  - 非法轮询阈值会提前报错。
- `utils/util.py`
  - 清理群聊 @ 文本时不再因为找不到前缀直接崩。
  - 图片下载增加超时和 HTTP 错误检查。

## 还没优化完的点

- 管理员权限仍按备注名/昵称判断，改名后会失效。
- 好友/群聊白名单仍按备注名/群名判断，改名后会失效。
- `wxbot.py` 仍偏胖，可以继续拆分：
  - 微信消息适配层
  - 绘图服务
  - 回复发送服务
  - 权限服务
- `utils/util.py` 仍是杂项工具集合，可以继续拆。
- 还没有正式 pytest 测试目录，目前主要靠手动脚本验证。
