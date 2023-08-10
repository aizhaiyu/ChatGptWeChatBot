from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool,FileSearchTool,YouTubeSearchTool
from langchain.agents import initialize_agent, AgentType
from langchain.schema import AIMessage,HumanMessage
import json
import os


llm=ChatOpenAI(temperature=0)

def testTmp():
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
                "description":"描述绘画的详细信息"
                }
            },
        }
    }
    ]
    return json


res=llm.predict_messages([HumanMessage(content="我想画一个漂亮的日本女孩")],functions=testTmp())
# p=res.additional_kwargs["function_call"]["arguments"]
print(res)



