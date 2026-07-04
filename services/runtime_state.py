import json
import logging
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from config.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


@dataclass
class RuntimeState:
    group_chat_list: list
    friend_chat_list: list
    group_role: str
    friend_role: str
    group_model: str
    friend_model: str

    def to_dict(self):
        return {
            'group_chat_list': list(self.group_chat_list or []),
            'friend_chat_list': list(self.friend_chat_list or []),
            'group_role': self.group_role,
            'friend_role': self.friend_role,
            'group_model': self.group_model,
            'friend_model': self.friend_model,
        }


class RuntimeStateStore:
    def __init__(self, state_file='data/runtime_state.json'):
        path = Path(state_file)
        if not path.is_absolute():
            path = PROJECT_ROOT / path

        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, config):
        if not self.path.exists():
            return self._from_config(config)

        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load runtime state %s: %s", self.path, exc)
            return self._from_config(config)

        return RuntimeState(
            group_chat_list=self._list_value(data, 'group_chat_list', config.GroupChatList),
            friend_chat_list=self._list_value(data, 'friend_chat_list', config.FriendChatList),
            group_role=self._value(data, 'group_role', config.GroupChatRole),
            friend_role=self._value(data, 'friend_role', config.FriendChatRole),
            group_model=self._value(data, 'group_model', config.model_name),
            friend_model=self._value(data, 'friend_model', config.model_name),
        )

    def save(self, state):
        payload = state.to_dict()
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        with NamedTemporaryFile('w', encoding='utf-8', delete=False, dir=self.path.parent) as tmp:
            tmp.write(serialized)
            tmp_path = Path(tmp.name)

        tmp_path.replace(self.path)

    def _from_config(self, config):
        return RuntimeState(
            group_chat_list=list(config.GroupChatList or []),
            friend_chat_list=list(config.FriendChatList or []),
            group_role=config.GroupChatRole,
            friend_role=config.FriendChatRole,
            group_model=config.model_name,
            friend_model=config.model_name,
        )

    def _value(self, data, key, default):
        value = data.get(key)
        return default if value is None else value

    def _list_value(self, data, key, default):
        value = data.get(key)
        if value is None:
            return list(default or [])
        if isinstance(value, list):
            return value
        return list(default or [])
