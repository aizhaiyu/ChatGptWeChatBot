import json
import requests

class SDClient:
    def __init__(self):
        self.url = "https://chatgpt.87youxi.cn/StableDiffusion/sdapi.php"
        self.api_key = 112233445566
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_key)
        }

    def generate_response(self, prompt):
        postdata = {
            "prompt": prompt,
            "n": 0.5,
            "size": "1024x1024"
        }
        postdata = json.dumps(postdata)

        response = requests.post(self.url, headers=self.headers, data=postdata)

        if response.status_code == 200:
            responsedata = response.json()
            if 'error' in responsedata:
                errcode = responsedata['error']['code']
                errmsg = responsedata['error']['message']
                if errmsg.startswith("Rate limit reached"):
                    errcode = "rate_limit_reached"
                if errmsg.startswith("Your access was terminated"):
                    errcode = "access_terminated"
                if errmsg.startswith("You didn't provide an API key"):
                    errcode = "no_api_key"
                if errmsg.startswith("You exceeded your current quota"):
                    errcode = "insufficient_quota"
                if errmsg.startswith("That model is currently overloaded"):
                    errcode = "model_overloaded"
                if errmsg.startswith("The server had an error"):
                    errcode = "server_overloaded"
                return errcode
            else:
                answer = responsedata
                if 'data' in answer and len(answer['data']) > 0 and 'url' in answer['data'][0]:
                    return answer['data'][0]['url']
                else:
                    return 'error'
        else:
            return 'HTTP Error: ' + str(response.status_code)


# client = SDClient()
# prompt = "A beautiful girl"  # 提示词，需要英文
# response = client.generate_response(prompt)
# print(response)
