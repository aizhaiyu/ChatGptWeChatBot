# coding:utf-8
from lib import itchat
from utils.instruct import Instruct
from datetime import datetime
from time import sleep
from plugins.openai.role import DrawingGenerator, normalize_openai_base_url
from utils.util import Common, Util
from utils.message import split_chat_reply
from services.admin_service import AdminService
from services.chat_service import ChatService
import config.log

logger = config.log.setup_logging("logs/app.log")

REPLY_PART_DELAY_SECONDS = 0.8


class WxBot:
    def __init__(self):
        self.instruct = Instruct()
        self.config = Util.get_config()
        self.chat_service = ChatService(self.config)
        self.admin_service = AdminService(self.config, self.chat_service)
        self.Draw = DrawingGenerator(
            self.config.openai_api_key[0], self.config.openai_api_base)
        self.key = iter(Util.get_ai_key())

    def handle_group_chat(self, msg):
        '''
        群聊
        '''
        if not msg.isAt:
            return None
        
        group_id = msg['FromUserName']
        group = itchat.search_chatrooms(userName=group_id)
        group_name = group.get('RemarkName', '') or group.get('NickName', '')

        # 判断群聊是否开启，并且是否是全部开启
        if not self.admin_service.is_group_enabled(group_name):
            logger.info(f'\n群聊 {group_name} 不在启用列表，已忽略')
            return None
        
        result = Util.cleanAt(itchat, msg.text)
        fun_name, result = self.instruct.question(result)

        logger.info(
            f'\n收到来自群 {group_name} 的消息\n发起人：{msg.actualNickName}\n内容：{msg.text}\n处理内容：{result}')

        if fun_name == self.instruct.isImg.__name__:
            self.sd_draw_image(msg, result, msg.actualNickName)
        elif fun_name == self.instruct.isHelp.__name__:
            self.send_message(msg.user, result)
        elif fun_name == self.instruct.admin.__name__:
            self.process_admin_command(msg, result, is_group=True)
        elif Util.check_char_in_list(result, self.config.draw):
            self.openai_draw_image(msg, result, msg.actualNickName)
        else:
            session_id = self.build_group_session_id(group_id, msg['ActualUserName'])
            display_name = f"{group_name}/{msg.actualNickName}"
            self.chat_with_gpt(msg.user, result, msg.actualNickName, session_id, display_name)
    
    def welcome_group_chat(self, msg):
        '''
        群聊欢迎监听
        '''
        logger.info("收到群聊通知消息：%s", msg)

    def handle_friend_chat(self, msg):
        '''
        私聊
        '''
        # 获取自己的 UserName
        myUserName = itchat.get_friends(update=True)[0]["UserName"]
        # 检查消息是否是自己发送的
        if msg['FromUserName'] == myUserName:
            return None
        
        fromName = msg['User']['RemarkName'] or msg['User']['NickName']
        if not self.admin_service.is_friend_enabled(fromName):
            logger.info(f'\n私聊人 {fromName} 不在启用列表，已忽略')
            return None

        fun_name, result = self.instruct.question(msg.text)

        logger.info(
            f'\n私聊人：{fromName}\n内容：{msg.text}\n处理内容：{result}')

        if fun_name == self.instruct.isImg.__name__:
            self.sd_draw_image(msg, result)
        elif fun_name == self.instruct.isHelp.__name__:
            self.send_message(msg.user, result)
        elif fun_name == self.instruct.admin.__name__:
            self.process_admin_command(msg, result, is_group=False)
        elif Util.check_char_in_list(result, self.config.draw):
            self.openai_draw_image(msg, result)
        else:
            self.chat_with_gpt(msg.user, result, session_id=msg['FromUserName'], display_name=fromName)

    def sd_draw_image(self, msg, result, actualNickName=None):
        # 下载图片
        current_time = datetime.now()
        Common().dowImg(result)
        new_time = datetime.now()
        time_diff = new_time - current_time
        txt = f'@{actualNickName}\u2005 绘图成功 \n耗时：{time_diff.total_seconds()}秒'
        logger.info(txt)
        msg.user.send(txt)
        msg.user.send('@img@./img/sd.png')

    def openai_draw_image(self, msg, result, actualNickName=None):
        # 生成绘图
        current_time = datetime.now()
        self.Draw.set_api_key(next(self.key))
        result = self.Draw.generate_drawing(result)
        Common().dowImg(result)
        new_time = datetime.now()
        time_diff = new_time - current_time
        txt = f'@{actualNickName}\u2005 绘图成功 \n耗时：{time_diff.total_seconds()}秒'
        logger.info(txt)
        msg.user.send(txt)
        msg.user.send('@img@./img/sd.png')

    def send_message(self, user, message):
        # 发送帮助信息
        user.send(message)
        
    def process_admin_command(self, msg, result, is_group=False):
        command = result
        # 获取发起人的 UserName是否为管理
        name = msg.get('ActualUserName') or msg.get('FromUserName')
        if not self.get_friend_info(name):
            msg.user.send("权限不足")
            return None

        msg.user.send(self.admin_service.handle(command, is_group=is_group))

    

    def chat_with_gpt(self, user, message, actualNickName=None, session_id=None, display_name=''):
        """
        使用 GPT 模型来回复消息。

        参数:
        user: 发送消息的用户对象。
        message (str): 用户发送的消息文本。
        actualNickName (str, 可选): 发送消息的用户的昵称。
        """
        is_group = actualNickName is not None
        try:
            res = self.chat_service.reply(message, session_id, display_name, is_group=is_group)
        except Exception as exc:
            logger.exception("GPT reply failed for %s: %s", display_name or session_id, exc)
            res = f"回复失败：{exc}"

        self.send_split_reply(user, res, actualNickName=actualNickName)

    def send_split_reply(self, user, message, actualNickName=None):
        parts = split_chat_reply(message, max_parts=5, max_chars=180)
        if not parts:
            return

        if actualNickName is not None:
            user.send(f'@{actualNickName}\u2005\n{parts[0]}')
            for part in parts[1:]:
                sleep(REPLY_PART_DELAY_SECONDS)
                user.send(part)
        else:
            user.send(parts[0])
            for part in parts[1:]:
                sleep(REPLY_PART_DELAY_SECONDS)
                user.send(part)

    def build_group_session_id(self, group_id, member_id):
        return f"group:{group_id}:member:{member_id}"
            
    def get_friend_info(self,username):
        '''
        usernanme找查好友是否为管理
        '''
        friend = itchat.search_friends(userName=username)
        if friend:
            name = friend["RemarkName"] or friend["NickName"]
            return name in self.config.admin

        return False
        
    def run(self):
        try:
            # 注册群聊消息处理函数
            @itchat.msg_register('Text', isGroupChat=self.config.isGroupChat)
            def text_GroupChat(msg):
                self.handle_group_chat(msg)
            # # 注册欢迎群聊消息处理函数
            # @itchat.msg_register('Note', isGroupChat=self.config.isGroupChat)
            # def welcome_GroupChat(msg):
            #     self.welcome_group_chat(msg)

            # 注册私聊消息处理函数
            @itchat.msg_register('Text', isFriendChat=self.config.isFriendChat)
            def text_FriendChat(msg):
                self.handle_friend_chat(msg)

        except Exception as e:
            logger.exception(f'An error occurred:{e}')

        itchat.auto_login(hotReload=True,enableCmdQR=self.config.system)
        itchat.run()

def main():
    base = Util.get_config().openai_api_base
    if base is not None:
        import os
        os.environ["OPENAI_API_BASE"] = normalize_openai_base_url(base)
    WxBot().run()
    
if __name__ == '__main__':
    main()
