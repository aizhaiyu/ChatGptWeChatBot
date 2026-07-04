from plugins.openai.role import ChatGpt
from utils.generateList import GenerateList
from utils.memory_store import MemoryStore
from services.runtime_state import RuntimeStateStore


class ChatService:
    def __init__(self, config):
        self.config = config
        self.group_role = config.GroupChatRole
        self.friend_role = config.FriendChatRole
        self.group_model = config.model_name
        self.friend_model = config.model_name
        self.runtime_state_store = RuntimeStateStore()
        self.key_generator = GenerateList(config.openai_api_key, config.threshold).next_item
        self.memory_store = MemoryStore(
            config.memory_dir,
            recent_limit=config.memory_recent_limit,
            compress_threshold=config.memory_compress_threshold,
            enabled=config.memory_enabled,
        )
        self.load_runtime_state()

    def load_runtime_state(self):
        state = self.runtime_state_store.load(self.config)
        self._apply_runtime_state(state)

    @property
    def runtime_state(self):
        return self._runtime_state

    def _apply_runtime_state(self, state):
        self._runtime_state = state
        self.group_role = state.group_role
        self.friend_role = state.friend_role
        self.group_model = state.group_model
        self.friend_model = state.friend_model

    def update_runtime_state(self, group_chat_list=None, friend_chat_list=None):
        if group_chat_list is not None:
            self._runtime_state.group_chat_list = list(group_chat_list)
        if friend_chat_list is not None:
            self._runtime_state.friend_chat_list = list(friend_chat_list)
        self._runtime_state.group_role = self.group_role
        self._runtime_state.friend_role = self.friend_role
        self._runtime_state.group_model = self.group_model
        self._runtime_state.friend_model = self.friend_model
        self.runtime_state_store.save(self._runtime_state)

    def set_role(self, role, is_group):
        if is_group:
            self.group_role = role
        else:
            self.friend_role = role
        self._runtime_state.group_role = self.group_role
        self._runtime_state.friend_role = self.friend_role
        self.runtime_state_store.save(self._runtime_state)

    def set_model(self, model, is_group):
        if is_group:
            self.group_model = model
        else:
            self.friend_model = model
        self._runtime_state.group_model = self.group_model
        self._runtime_state.friend_model = self.friend_model
        self.runtime_state_store.save(self._runtime_state)

    def reply(self, message, session_id, display_name='', is_group=False):
        gpt = self._new_client(is_group)
        memory = self.memory_store.load(session_id, display_name) if session_id else None

        response = gpt.chat_ai_usage(message, memory=memory)

        if memory is not None:
            memory = self.memory_store.append_turn(memory, message, response)
            memory = self.memory_store.compress_if_needed(memory, gpt.summarize_memory)
            self.memory_store.save(memory)

        return response

    def _new_client(self, is_group):
        return ChatGpt(
            next(self.key_generator),
            role=self.group_role if is_group else self.friend_role,
            model=self.group_model if is_group else self.friend_model,
            temperature=self.config.temperature,
            openai_api_base=self.config.openai_api_base,
        )
