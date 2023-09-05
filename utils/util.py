import os
# from interfaces.Itchat import WeChatBotWrapper
from config.config import Config
from utils.generateList import GenerateList
import requests

class Util:
    
    _config = None #配置
    _ai_key = None #key对象
    
    @staticmethod
    def get_config():
        if Util._config is None:
            Util._config = Config()  # Replace 'config/config.yaml' with your actual path
        return Util._config
    
    @staticmethod
    def get_ai_key():
        '''
        使用方法：\n
        while True:\n
        key = next(generator)\n
        if key is not None:\n
            print("key:", key)
        '''
        if Util._ai_key is None:
            con=Util.get_config()
            Util._ai_key = GenerateList(con.openai_api_key,con.threshold).generate_list
        return Util._ai_key
    
    # WeChatBot=WeChatBotWrapper()
    
    @staticmethod
    def cleanAt(message):
        '''
        # 去除@符号和名称
        '''
        name=Util.get_config().name
        # @null  /img 你在干嘛 获取:/img 你在干嘛
        prefix = f'@{name}'
        message = message[message.index(prefix) + len(prefix):]#去掉艾特
        return message.replace(f'\u2005', '')
    

    @staticmethod
    def check_char_in_list(text, char_list):
        return bool(set(text) & set(char_list))


class Common:
    @staticmethod
    def dowImg(url):
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        }
        path = "./img/sd.png"
        response = requests.get(url, headers=header)  # 请求
        with open(f"{path}", "wb") as f:  # wb二进制
            f.write(response.content)
        return True
    
    

