
class Admin:
    def __init__(self):
        self.instruct = {'$role': self.admin_role}  # 指令映射

    def use(self, text):
        '''
        获取提问，判断是否存在指令，不存在则返回描述语句
        Args:
            text(string):内容
        Returns:
            string
        '''
        #判断是否包含指令
        # 去掉前面的空格
        result = text.lstrip()
        for key in self.instruct.keys():
            if result.find(key) != -1:
                #存在
                return self.instruct[key](result)
        else:
            #返回原本 判断是否存在空
            return self.admin()
        
    def admin(self):
        text= f'''#admin 操作指令:使用管理指令\n
        操作指令:
        $role 角色描述:角色扮演
        $addGroupChat 群聊名称:添加可用群聊
        $addFriendChat 好友名称:添加可私聊好友
        $delGroupChat 排除群聊:从可用群聊中移除
        $delFriendChat 排除好友:排除可私聊好友
        $drawModel 绘画模型:更改绘画使用的模型
        '''
        # 去除每行开头的空格
        formatted_text = '\n'.join(line.lstrip() for line in text.split('\n'))
        return (self.admin.__name__, formatted_text)

    def admin_role(self, text):
        if text.startswith("$role"):
            index =text.find('$role')
            if index != -1:
                result = text[index + len("$role"):].strip()
                return (self.admin_role.__name__,result)
        return self.admin_role.__name__, None




