from admin.admin import AdminAction


class AdminService:
    def __init__(self, config, chat_service):
        self.chat_service = chat_service
        self.group_chat_list = list(chat_service.runtime_state.group_chat_list)
        self.friend_chat_list = list(chat_service.runtime_state.friend_chat_list)

    def is_group_enabled(self, group_name):
        return not self.group_chat_list or group_name in self.group_chat_list

    def is_friend_enabled(self, friend_name):
        return not self.friend_chat_list or friend_name in self.friend_chat_list

    def handle(self, command, is_group=False):
        if not command.is_valid:
            return command.message

        if command.action == AdminAction.HELP:
            return command.message
        if command.action == AdminAction.SET_ROLE:
            self.chat_service.set_role(command.argument, is_group=is_group)
            return "角色设置成功"
        if command.action == AdminAction.SET_MODEL:
            self.chat_service.set_model(command.argument, is_group=is_group)
            return "模型更换成功"
        if command.action == AdminAction.ADD_FRIEND_CHAT:
            result = self._add_item(self.friend_chat_list, command.argument, "好友")
            self._sync_runtime_state()
            return result
        if command.action == AdminAction.ADD_GROUP_CHAT:
            result = self._add_item(self.group_chat_list, command.argument, "群聊")
            self._sync_runtime_state()
            return result
        if command.action == AdminAction.DEL_FRIEND_CHAT:
            result = self._remove_item(self.friend_chat_list, command.argument, "好友")
            self._sync_runtime_state()
            return result
        if command.action == AdminAction.DEL_GROUP_CHAT:
            result = self._remove_item(self.group_chat_list, command.argument, "群聊")
            self._sync_runtime_state()
            return result

        return "设置失败或指令错误"

    def _add_item(self, items, item, label):
        if item in items:
            return f"{label}{item}已存在"

        items.append(item)
        return f"添加{item}成功"

    def _remove_item(self, items, item, label):
        if item not in items:
            return f"{label}{item}不在启用列表"

        items[:] = [current for current in items if current != item]
        return f"去除{item}成功"

    def _sync_runtime_state(self):
        self.chat_service.update_runtime_state(self.group_chat_list, self.friend_chat_list)
