import itchat
from utils.instruct import Instruct
from datetime import datetime, timedelta
from plugins.openai.role import ChatGpt, DrawingGenerator
from utils.util import Common, Util
from admin.admin import Admin
import config.log
import os

logger = config.log.setup_logging("logs/app.log")


class WxBot:
    def __init__(self):
        self.instruct = Instruct()
        self.config = Util.get_config()
        self.GroupGptList=Util.get_config().GroupChatList
        self.FriendGptList=Util.get_config().FriendChatList
        # 初始化 ChatGpt 实例，用于群聊
        self.GroupGpt = self.set_role_model(self.config.GroupChatRole,self.config.model_name)
        # 初始化 ChatGpt 实例，用于私聊
        self.FriendGpt = self.set_role_model(self.config.FriendChatRole,self.config.model_name)
        # 初始化 DrawingGenerator 实例，用于生成绘图
        self.Draw = DrawingGenerator(
            self.config.openai_api_key[0], self.config.openai_api_base)
        
        self.key = iter(Util.get_ai_key())
        
    def set_role_model(self, role,model_name):
        '''
        设置角色or模型
        '''
        return ChatGpt(
            self.config.openai_api_key[0],
            role=role,
            openai_api_base=self.config.openai_api_base,
            temperature=self.config.temperature,
            model=model_name
        )

    def handle_group_chat(self, msg):
        '''
        群聊
        '''
        if msg.isAt:
            
            # for chat in itchat.get_chatrooms(update=True):
            #     pass
            result = Util.cleanAt(msg.text)
            fun_name, result = self.instruct.question(result)
            
            logger.info(
                f'\n发起人：{msg.actualNickName}\n内容：{msg.text}\n处理内容：{result}')

            if fun_name == self.instruct.isImg.__name__:
                self.sd_draw_image(msg, result, msg.actualNickName)
            elif fun_name == self.instruct.isHelp.__name__:
                self.send_message(msg.user, result)
            elif fun_name == self.instruct.admin.__name__:
                self.process_admin_command(msg, result, msg.actualNickName)
            elif Util.check_char_in_list(result, self.config.draw):
                self.openai_draw_image(msg, result, msg.actualNickName)
            else:
                self.chat_with_gpt(msg.user, result, msg.actualNickName)

    def handle_friend_chat(self, msg):
        '''
        私聊
        '''
        fromName = msg['User']['RemarkName']
        friend = self.FriendGptList
        
        if (fromName in friend) or len(friend) == 0:
            fun_name, result = self.instruct.question(msg.text)

            logger.info(
                f'\n私聊人：{fromName}\n内容：{msg.text}\n处理内容：{result}')

            if fun_name == self.instruct.isImg.__name__:
                self.sd_draw_image(msg, result)
            elif fun_name == self.instruct.isHelp.__name__:
                self.send_message(msg.user, result)
            elif fun_name == self.instruct.admin.__name__:
                self.process_admin_command(msg, result, fromName)
            elif Util.check_char_in_list(result, self.config.draw):
                self.openai_draw_image(msg, result)
            else:
                self.chat_with_gpt(msg.user, result)

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
        result = self.Draw.generate_drawing(result)
        self.Draw.api_key = next(self.key)#轮询
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

    def process_admin_command(self, msg, result, actualNickName=None):
        fun_admin, text = result
        if actualNickName == self.config.admin:
            if fun_admin == Admin.admin.__name__:
                msg.user.send(text)
            elif fun_admin == Admin.admin_role.__name__ and text is not None:
                # 设置角色
                self.GroupGpt = self.set_role_model(text,self.config.model_name)
                msg.user.send("角色设置成功")
                
            elif fun_admin in [
                Admin.del_GroupChat.__name__,
                Admin.del_FriendChat.__name__,
            ]:
                self.del_list(fun_admin, text)
            elif fun_admin in [
                Admin.add_FriendChat.__name__,
                Admin.add_GroupChat.__name__,
            ]:
                self.add_list(fun_admin, text)
            else:
                msg.user.send("设置失败或指令错误")
        else:
            msg.user.send("权限不足")
            
            
    def del_list(self,type,item):
        if type == Admin.del_FriendChat.__name__:
            self.FriendGptList = [x for x in self.FriendGptList if x != item]
            return self.FriendGptList
        else:
            self.GroupGptList = [x for x in self.GroupGptList if x != item]
            return self.GroupGptList
        
    def add_list(self,type,item):
        if type == Admin.add_FriendChat.__name__:
            self.FriendGptList.append(item)
        else:
            self.GroupGptList.append(item)

    

    def chat_with_gpt(self, user, message, actualNickName=None):
        key=next(self.key)
        print(key)
        os.environ["OPENAI_API_KEY"] = key#轮询
        # 使用 GPT 进行聊天
        if actualNickName is not None:
            res = self.GroupGpt.chat_ai_usage(message)
            user.send(f'@{actualNickName}\u2005\n{res}')
        else:
            res = self.FriendGpt.chat_ai_usage(message)
            user.send(res)

    def run(self):
        try:
            # 注册群聊消息处理函数
            @itchat.msg_register('Text', isGroupChat=self.config.isGroupChat)
            def text_GroupChat(msg):
                self.handle_group_chat(msg)

            # 注册私聊消息处理函数
            @itchat.msg_register('Text', isFriendChat=self.config.isFriendChat)
            def text_FriendChat(msg):
                self.handle_friend_chat(msg)

        except Exception as e:
            logger.exception(f'An error occurred:{e}')

        itchat.auto_login(hotReload=True,enableCmdQR=self.config.system)
        itchat.run()

def main():
    pass
    
if __name__ == '__main__':
    os.environ["OPENAI_API_BASE"] = Util.get_config().openai_api_base
    WxBot().run()
