from dataclasses import dataclass
from enum import Enum
from textwrap import dedent


class AdminAction(Enum):
    HELP = "help"
    SET_ROLE = "set_role"
    SET_MODEL = "set_model"
    ADD_GROUP_CHAT = "add_group_chat"
    ADD_FRIEND_CHAT = "add_friend_chat"
    DEL_GROUP_CHAT = "del_group_chat"
    DEL_FRIEND_CHAT = "del_friend_chat"
    INVALID = "invalid"


@dataclass(frozen=True)
class AdminCommand:
    action: AdminAction
    argument: str = ""
    message: str = ""

    @property
    def is_valid(self):
        return self.action != AdminAction.INVALID


class Admin:
    HELP_TEXT = dedent(
        """\
        #admin 操作指令:使用管理指令

        操作指令:
        $role 角色描述:角色扮演
        $addGroupChat 群聊名称:添加可用群聊
        $addFriendChat 好友名称:添加可私聊好友
        $delGroupChat 群聊名称:从可用群聊中移除
        $delFriendChat 好友名称:排除可私聊好友
        $model 聊天模型:更改聊天使用的模型
        """
    )

    _COMMANDS = {
        "$role": (AdminAction.SET_ROLE, "角色描述"),
        "$model": (AdminAction.SET_MODEL, "聊天模型"),
        "$addGroupChat": (AdminAction.ADD_GROUP_CHAT, "群聊名称"),
        "$addFriendChat": (AdminAction.ADD_FRIEND_CHAT, "好友名称"),
        "$delGroupChat": (AdminAction.DEL_GROUP_CHAT, "群聊名称"),
        "$delFriendChat": (AdminAction.DEL_FRIEND_CHAT, "好友名称"),
    }

    def parse(self, text):
        content = self._normalize_admin_text(text)
        if not content:
            return AdminCommand(AdminAction.HELP, message=self.HELP_TEXT)

        command, _, argument = content.partition(" ")
        if command not in self._COMMANDS:
            return AdminCommand(
                AdminAction.INVALID,
                message=f"未知管理员指令：{command}\n\n{self.HELP_TEXT}",
            )

        action, argument_name = self._COMMANDS[command]
        argument = argument.strip()
        if not argument:
            return AdminCommand(
                AdminAction.INVALID,
                message=f"{command} 缺少{argument_name}\n\n{self.HELP_TEXT}",
            )

        return AdminCommand(action, argument=argument)

    def _normalize_admin_text(self, text):
        if not isinstance(text, str):
            return ""

        content = text.strip()
        if content.startswith("#admin"):
            content = content[len("#admin"):]
        return content.strip()
