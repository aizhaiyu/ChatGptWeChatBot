import json

from langchain_openai import ChatOpenAI
from openai import OpenAI


def normalize_openai_base_url(openai_api_base):
    if not openai_api_base:
        return None

    base_url = openai_api_base.rstrip("/")
    if base_url.endswith("/v1"):
        return base_url
    return f"{base_url}/v1"


class ChatGpt:
    def __init__(self, openai_api_key, role='', model='gpt-3.5-turbo', temperature=0.9, openai_api_base=None):
        self.role = role
        self.model = model
        self.temperature = temperature
        self.openai_api_base = normalize_openai_base_url(openai_api_base)
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=openai_api_key,
            base_url=self.openai_api_base,
        )

    @staticmethod
    def setRole(gpt, role):
        gpt.role = role

    def chat_ai_usage(self, user_input, username='', memory=None):
        messages = [
            ("system", self.role or "你是一个自然、准确的微信私聊对象。"),
            ("system", "回复风格要像真人微信聊天，尽量用 2 到 5 句短句回答。可以分多句输出，句子之间保持自然的中文句号或换行，不要一次写成一大段。"),
        ]
        if memory:
            if memory.facts:
                facts = "\n".join(f"- {fact}" for fact in memory.facts)
                messages.append(("system", f"以下是你与当前用户的稳定事实记忆，优先用于保持人设和上下文一致：\n{facts}"))
            if memory.summary:
                messages.append(("system", f"以下是你与当前用户的对话摘要，主要用于理解近期话题背景：\n{memory.summary}"))
            for item in memory.recent_messages:
                role = item.get('role')
                content = item.get('content')
                if role in ('user', 'assistant') and content:
                    messages.append(("human" if role == "user" else "ai", content))

        messages.append(("human", f"根据用户提问: {user_input}\n认真回答上述问题。"))
        response = self.llm.invoke(messages)
        return response.content

    def summarize_memory(self, current_summary, current_facts, messages):
        history = "\n".join(
            f"{item.get('role', '')}: {item.get('content', '')}"
            for item in messages
            if item.get('content')
        )
        prompt = (
            "请把以下对话整理成两层记忆，并且只输出 JSON，不要输出 Markdown。\n"
            "JSON 格式必须是：{\"facts\":[\"...\"],\"summary\":\"...\"}\n\n"
            "facts 是稳定事实记忆，只保留后续长期有用的信息，例如：用户姓名、身份、偏好、关系、长期目标、明确要求、重要事件。"
            "不要保存寒暄、一次性问题、短期情绪、无意义细节。facts 最多 30 条，每条不超过 40 个中文字符。\n"
            "summary 是对话摘要，用于理解旧对话背景，控制在 300 字以内。\n"
            "如果新对话修正了旧事实，请用新事实覆盖旧事实，不要保留冲突项。\n\n"
            f"已有摘要：\n{current_summary or '无'}\n\n"
            f"已有事实：\n{json.dumps(current_facts or [], ensure_ascii=False)}\n\n"
            f"新增对话：\n{history}"
        )
        response = self.llm.invoke([
            ("system", "你负责把微信聊天历史整理成稳定事实记忆和对话摘要。"),
            ("human", prompt),
        ])
        return self._parse_memory_update(response.content)

    def _parse_memory_update(self, content):
        content = self._strip_json_markdown(content.strip())
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return {
                "facts": [],
                "summary": content.strip(),
            }

        facts = payload.get("facts") or []
        if not isinstance(facts, list):
            facts = []

        summary = payload.get("summary") or ""
        if not isinstance(summary, str):
            summary = ""

        return {
            "facts": [item.strip() for item in facts if isinstance(item, str) and item.strip()],
            "summary": summary.strip(),
        }

    def _strip_json_markdown(self, content):
        if content.startswith("```"):
            lines = content.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return content


class DrawingGenerator:
    '''
    绘图
    '''
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = normalize_openai_base_url(api_base)

    def set_api_key(self, api_key):
        self.api_key = api_key

    def generate_drawing(self, prompt):
        client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
        )
        return response.data[0].url


if __name__ == '__main__':
    role = "你是一个简洁、准确的微信助手。"
    gpt = ChatGpt("sk-your-openai-api-key", role=role)
    print(gpt.chat_ai_usage("你好"))
