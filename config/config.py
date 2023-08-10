import yaml


class Config:
    def __init__(self, config_file='config/config.yaml'):
        self.config_data = self._load_config(config_file)

    def _load_config(self, config_file):
        with open(config_file, 'rb') as file:
            config_data = yaml.safe_load(file)
        return config_data

    @property
    def admin(self):
        return self.config_data['wx_bot']['admin']

    @property
    def name(self):
        return self.config_data['wx_bot']['name']

    @property
    def threshold(self):
        return self.config_data['openai']['threshold']

    @property
    def isGroupChat(self):
        return self.config_data['wx_bot']['chat']['isGroupChat']

    @property
    def isFriendChat(self):
        return self.config_data['wx_bot']['chat']['isFriendChat']

    @property
    def FriendChatList(self):
        return self.config_data['wx_bot']['chat']['FriendChatList']

    @property
    def GroupChatList(self):
        return self.config_data['wx_bot']['chat']['GroupChatList']

    @property
    def GroupChatRole(self):
        return self.config_data['wx_bot']['chat']['GroupChatRole']

    @property
    def FriendChatRole(self):
        return self.config_data['wx_bot']['chat']['FriendChatRole']

    @property
    def openai_api_key(self):
        return self.config_data['openai']['openai_api_key']

    @property
    def openai_api_base(self):
        return self.config_data['openai']['openai_api_base']

    @property
    def model_name(self):
        return self.config_data['openai']['model_name']

    @property
    def temperature(self):
        return self.config_data['openai']['temperature']

    @property
    def draw(self):
        return self.config_data['openai']['draw']

    @property
    def timeout(self):
        return self.config_data['timeout']
