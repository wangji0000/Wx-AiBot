import configparser
import os
import requests
from wxauto import WeChat

# 获取配置文件
config = configparser.RawConfigParser()
with open('conf.ini', 'r', encoding='utf-8') as f:
    config.read_file(f)

# 读取users.txt加载监听用户
MONITOR_LIST = []
if not os.path.exists("users.txt"):
    fp = open("users.txt", encoding="utf-8", mode='w')
    fp.close()
else:
    fp = open("users.txt", encoding="utf-8", mode='r')
    for line in fp:
        line = line.strip()
        if not line:
            continue
        MONITOR_LIST.append(line)
    fp.close()

# 1.打开微信
wx = WeChat()

# 2.监听账户列表（好友名称）
for ele in MONITOR_LIST:
    wx.AddListenChat(who=ele, savepic=True)


# 3.监听消息
def deepseek(content):
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }
    headers = {
        "Authorization": f"Bearer {config['API']['key']}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    data = response.json()

    content = data['choices'][0]['message']['content']
    print('ai回答：', content)

    return content


def send_msg(chat, content):
    chat.SendMsg(deepseek(content))  # 发送消息


def listen_and_reply():
    while True:
        msgs = wx.GetListenMessage()
        for chat in msgs:
            one_msgs = msgs.get(chat)
            for msg in one_msgs:
                if msg.type == 'time' or msg.type == 'self' or msg.type == 'sys':
                    continue
                print(msg)
                content = msg.content
                # 发送消息
                send_msg(chat, content)


listen_and_reply()
