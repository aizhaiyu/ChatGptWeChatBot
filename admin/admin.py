
class Admin:
    def __init__(self):
        # 指令映射
        self.instruct = {'$role': self.admin_role, '$addGroupChat':self.add_GroupChat, \
                         '$addFriendChat':self.add_FriendChat, '$delGroupChat':self.del_GroupChat,\
                         '$delFriendChat': self.del_FriendChat, '$model': self.admin_model}

    def use(self, text):
        '''
        获取提问，判断是否存在指令，不存在则返回描述语句
        Args:
            text(string):内容
        Returns:
            string
        '''
        # 判断是否包含指令，去掉前面的空格
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
        $model 聊天模型:更改聊天使用的模型
        '''
        # 去除每行开头的空格
        formatted_text = '\n'.join(line.lstrip() for line in text.split('\n'))
        return (self.admin.__name__, formatted_text)

    def admin_role(self, text):
        result = self.dateOp(text)
        return self.admin_role.__name__, result
    
    def admin_model(self, text):
        result = self.dateOp(text)
        return self.admin_model.__name__, result
    
    def del_FriendChat(self, text):
        result = self.dateOp(text)
        return self.del_FriendChat.__name__, result
    
    def del_GroupChat(self, text):
        result = self.dateOp(text)
        return self.del_GroupChat.__name__, result
    
    def add_FriendChat(self, text):
        result = self.dateOp(text)
        return self.add_FriendChat.__name__, result

    def add_GroupChat(self, text):
        result = self.dateOp(text)
        return self.add_GroupChat.__name__, result
        
    
    
    def dateOp(self, text):
        if text.startswith(text):
            index = text.find(text)
            return text[index + len(text):].strip() if index != -1 else None




