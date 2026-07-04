from dataclasses import dataclass
from pathlib import Path

import yaml

from config.paths import PROJECT_ROOT


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class ChatConfig:
    is_group_chat: bool
    is_friend_chat: bool
    group_chat_list: list
    friend_chat_list: list
    group_chat_role: str
    friend_chat_role: str


@dataclass(frozen=True)
class WxBotConfig:
    admin: list
    chat: ChatConfig


@dataclass(frozen=True)
class OpenAIConfig:
    model_name: str
    temperature: float
    threshold: int
    api_base: str
    api_keys: list
    draw_keywords: list


@dataclass(frozen=True)
class MemoryConfig:
    enabled: bool
    directory: str
    recent_limit: int
    compress_threshold: int


@dataclass(frozen=True)
class AppConfig:
    system: bool
    timeout: int
    wx_bot: WxBotConfig
    openai: OpenAIConfig
    memory: MemoryConfig


class Config:
    def __init__(self, config_file='config/config.yaml'):
        self.config_path = self._resolve_path(config_file)
        self.raw_data = self._load_yaml(self.config_path)
        self.settings = self._parse(self.raw_data)

    def _resolve_path(self, config_file):
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = PROJECT_ROOT / config_path
        return config_path

    def _load_yaml(self, config_path):
        if not config_path.exists():
            raise ConfigError(f"配置文件不存在：{config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            raise ConfigError(f"配置文件 YAML 格式错误：{config_path}: {exc}") from exc

        if not isinstance(data, dict):
            raise ConfigError(f"配置文件内容必须是 YAML 对象：{config_path}")
        return data

    def _parse(self, data):
        wx_bot = self._dict(data, 'wx_bot')
        chat = self._dict(wx_bot, 'chat')
        openai = self._dict(data, 'openai')
        memory = self._optional_dict(data, 'memory')

        chat_config = ChatConfig(
            is_group_chat=self._bool(chat, 'isGroupChat', True),
            is_friend_chat=self._bool(chat, 'isFriendChat', True),
            group_chat_list=self._list(chat, 'GroupChatList', []),
            friend_chat_list=self._list(chat, 'FriendChatList', []),
            group_chat_role=self._str(chat, 'GroupChatRole', ''),
            friend_chat_role=self._str(chat, 'FriendChatRole', ''),
        )

        openai_config = OpenAIConfig(
            model_name=self._str(openai, 'model_name', 'gpt-3.5-turbo'),
            temperature=self._float(openai, 'temperature', 0.9),
            threshold=self._int(openai, 'threshold', 1, minimum=1),
            api_base=self._str(openai, 'openai_api_base', ''),
            api_keys=self._non_empty_list(openai, 'openai_api_key'),
            draw_keywords=self._list(openai, 'draw', []),
        )

        memory_config = MemoryConfig(
            enabled=self._bool(memory, 'enabled', True),
            directory=self._str(memory, 'dir', 'data/memory'),
            recent_limit=self._int(memory, 'recent_limit', 12, minimum=2),
            compress_threshold=self._int(memory, 'compress_threshold', 16, minimum=4),
        )

        return AppConfig(
            system=self._bool(data, 'system', False),
            timeout=self._int(data, 'timeout', 30, minimum=1),
            wx_bot=WxBotConfig(
                admin=self._list(wx_bot, 'admin', []),
                chat=chat_config,
            ),
            openai=openai_config,
            memory=memory_config,
        )

    @property
    def admin(self):
        return self.settings.wx_bot.admin

    @property
    def threshold(self):
        return self.settings.openai.threshold

    @property
    def isGroupChat(self):
        return self.settings.wx_bot.chat.is_group_chat

    @property
    def isFriendChat(self):
        return self.settings.wx_bot.chat.is_friend_chat

    @property
    def FriendChatList(self):
        return self.settings.wx_bot.chat.friend_chat_list

    @property
    def GroupChatList(self):
        return self.settings.wx_bot.chat.group_chat_list

    @property
    def GroupChatRole(self):
        return self.settings.wx_bot.chat.group_chat_role

    @property
    def FriendChatRole(self):
        return self.settings.wx_bot.chat.friend_chat_role

    @property
    def openai_api_key(self):
        return self.settings.openai.api_keys

    @property
    def openai_api_base(self):
        return self.settings.openai.api_base

    @property
    def model_name(self):
        return self.settings.openai.model_name

    @property
    def temperature(self):
        return self.settings.openai.temperature

    @property
    def draw(self):
        return self.settings.openai.draw_keywords

    @property
    def timeout(self):
        return self.settings.timeout

    @property
    def system(self):
        return self.settings.system

    @property
    def memory_enabled(self):
        return self.settings.memory.enabled

    @property
    def memory_dir(self):
        return self.settings.memory.directory

    @property
    def memory_recent_limit(self):
        return self.settings.memory.recent_limit

    @property
    def memory_compress_threshold(self):
        return self.settings.memory.compress_threshold

    def _dict(self, data, key):
        value = data.get(key)
        if not isinstance(value, dict):
            raise ConfigError(f"配置项 {key} 必须是对象")
        return value

    def _optional_dict(self, data, key):
        value = data.get(key)
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ConfigError(f"配置项 {key} 必须是对象")
        return value

    def _str(self, data, key, default=''):
        value = data.get(key, default)
        if value is None:
            return default
        if not isinstance(value, str):
            raise ConfigError(f"配置项 {key} 必须是字符串")
        return value

    def _bool(self, data, key, default=False):
        value = data.get(key, default)
        if not isinstance(value, bool):
            raise ConfigError(f"配置项 {key} 必须是 true/false")
        return value

    def _int(self, data, key, default=0, minimum=None):
        value = data.get(key, default)
        if not isinstance(value, int):
            raise ConfigError(f"配置项 {key} 必须是整数")
        if minimum is not None and value < minimum:
            raise ConfigError(f"配置项 {key} 必须大于等于 {minimum}")
        return value

    def _float(self, data, key, default=0.0):
        value = data.get(key, default)
        if not isinstance(value, (int, float)):
            raise ConfigError(f"配置项 {key} 必须是数字")
        return float(value)

    def _list(self, data, key, default=None):
        value = data.get(key, default if default is not None else [])
        if value is None:
            return []
        if not isinstance(value, list):
            raise ConfigError(f"配置项 {key} 必须是列表")
        return value

    def _non_empty_list(self, data, key):
        value = self._list(data, key, [])
        if not value:
            raise ConfigError(f"配置项 {key} 不能为空")
        if not all(isinstance(item, str) and item.strip() for item in value):
            raise ConfigError(f"配置项 {key} 必须是非空字符串列表")
        return value
