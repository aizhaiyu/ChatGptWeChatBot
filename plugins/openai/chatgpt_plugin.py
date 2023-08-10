from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain#会话支持
from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationSummaryMemory  # 会话记忆功能
from langchain.callbacks import get_openai_callback#回调
import os


class ChatBot:
    total_token=0

    def __init__(self, temperature=0.5, model_name="gpt-3.5-turbo"):
        self.llm = ChatOpenAI(
            temperature=temperature,
            model_name=model_name,
            functions=self.testTmp()
        )
        self.conversation = ConversationChain(
            llm=self.llm,
            memory=ConversationBufferMemory()
        )
        self.summary_conversation = ConversationChain(
            llm=self.llm, memory=ConversationSummaryMemory(llm=self.llm)
        )
    def testTmp(self):
        '''
        Obtain time and date
        '''
        json=[
            {
            "name": "get_draw_description",
            "description": "获取画图或绘画的详细描述",
            "required":["draw_des"],
            "parameters":{
                "type": "object",
                "properties":{
                    "draw_des":{
                    "type": "string",
                    "description":"绘画的描述信息"
                    }
                },
            }
        }
        ]
        return json

    def chat_ai(self, query):
        with get_openai_callback() as cb:
            if self.total_token>2500:
                #基于token来回答，摘要
                result = self.summary_conversation.run(query)
            else:
                result = self.conversation.run(query)
            self.total_token += cb.total_tokens;
            return result, cb.total_tokens

    def chat_ai_usage(self, query):
        result, total_tokens = self.chat_ai(query)
        print(f"{result}\ntotal token: {total_tokens}")
        return result


def main(query):
    bot = ChatBot()
    s=bot.chat_ai_usage(query)
    print(s)
    

if __name__ == "__main__":
    main("画一个女孩")

#基于摘要记忆组件 优化token消耗
# summary_conversation=ConversationChain(llm=llm,memory=ConversationSummaryMemory(llm=llm))
# print(ChatAiUsage(summary_conversation, "写一个js轮播图"))
