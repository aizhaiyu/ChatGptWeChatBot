import plugins.sd as sd
from admin.admin import Admin
import re

class Instruct:
    def __init__(self):
        self.instruct = {'#help': self.isHelp,'帮助':self.isHelp,'#admin':self.admin,\
                         '/url': self.url,'/img': self.isImg}  # 指令映射

    def question(self, text):
        '''
        获取提问，判断是否存在指令，不存在则返回描述语句
        Args:
            text(string):内容
        Returns:
            string
        '''

        #判断是否包含指令
        # 提取第一个空格前面的内容
        result = extract_content(text)
        for key in self.instruct.keys():
            if result == key:
                return self.instruct[key](text)
        else:
            #返回原本 判断是否存在空
            return self.question.__name__, text
        

    def isImg(self, command):
        '''
        处理绘图指令
        '''
        index = command.find(" ")
        if index != -1:
            result = command[index + 1:]
            return sd.SDClient().generate_response(result)
        return self.isImg.__name__, "绘图描述格式错误！"
    
    
    def url(self,msg):
        return self.url.__name__,"待开发"
        
    def admin(self,msg):
        result = Admin().use(msg.replace("#admin", ''))
        return self.admin.__name__, result
    
    def isHelp(self, command):
        '''
        处理帮助指令
        '''
        text= f'''使用帮助\n
        常用指令:
        #help :回复使用教程
        #admin :管理员功能
        '可以直接叫我绘画哦'

        可用功能:
        /img 英文描述画面:使用Stable Diffusion绘画
        /url 网页链接 提问内容:自动总结网页内容，根据内容回答
        待开发
        '''
        # 去除每行开头的空格
        formatted_text = '\n'.join(line.lstrip() for line in text.split('\n'))
        return self.isHelp.__name__,formatted_text


def extract_content(string):
    # 去除两端空格
    string = string.strip()

    # 使用正则表达式匹配第一个空格前的内容
    match = re.match(r"([^ ]+)", string)

    if match:
        result = match.group(1)
    else:
        result = None

    return result
