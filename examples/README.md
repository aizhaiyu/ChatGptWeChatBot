# Examples

这里放未接入微信机器人主链路的实验代码。主程序只依赖：

- `wxbot.py`
- `services/chat_service.py`
- `plugins/openai/role.py`
- `plugins/sd.py`
- `utils/`

旧的 LangChain demo 已不再放在 `plugins/openai/` 下，避免升级 LangChain 后被误导入影响主程序。
