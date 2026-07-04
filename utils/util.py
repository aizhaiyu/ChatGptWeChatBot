from config.config import Config
from config.paths import IMAGE_DIR
from utils.generateList import GenerateList
import requests

class Util:
    
    _config = None #配置
    _ai_key = None #key对象
    
    @staticmethod
    def get_config():
        if Util._config is None:
            Util._config = Config()
        return Util._config
    
    @staticmethod
    def get_ai_key():
        '''
        使用方法：\n
        while True:\n
            key = next(generator)\n
            print("key:", key)
        '''
        if Util._ai_key is None:
            con = Util.get_config()
            Util._ai_key = GenerateList(con.openai_api_key, con.threshold).next_item
        return Util._ai_key
    
    
    @staticmethod
    def cleanAt(itchat, message):
        '''
        # 去除@符号和名称
        '''
        name = itchat.get_friends(update=True)[0]["NickName"]
        # @null  /img 你在干嘛 获取:/img 你在干嘛
        prefix = f'@{name}'
        if prefix not in message:
            return message.replace(f'\u2005', '').strip()

        message = message[message.index(prefix) + len(prefix):]
        return message.replace(f'\u2005', '')
    

    @staticmethod
    def check_char_in_list(text, char_list):
        if not text or not char_list:
            return False
        return any(keyword and keyword in text for keyword in char_list)


class Common:
    @staticmethod
    def dowImg(url):
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        }
        path = IMAGE_DIR / "sd.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, headers=header, timeout=30)
        response.raise_for_status()
        with open(path, "wb") as f:  # wb二进制
            f.write(response.content)
        return True
    
    
