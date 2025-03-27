import configparser
import os
import requests
import json
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
def deepseek_stream(content, chat):
    """使用流式API获取DeepSeek响应并发送消息"""
    url = "https://api.deepseek.com/v1/chat/completions"
    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": True,
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

    # 使用stream=True参数进行流式请求
    response = requests.request("POST", url, json=payload, headers=headers, stream=True)
    
    # 存储完整回复以便打印日志
    full_response = ""
    # 存储当前片段，当达到一定长度时发送
    current_chunk = ""
    chunk_size = 30  # 每次发送约30个字符
    
    # 处理流式响应
    for line in response.iter_lines():
        if line:
            # 移除 "data: " 前缀并解析JSON
            line = line.decode('utf-8')
            if line.startswith("data: "):
                if line == "data: [DONE]":
                    # 发送剩余内容
                    if current_chunk:
                        chat.SendMsg(current_chunk)
                    break
                
                try:
                    json_data = json.loads(line[6:])  # 去除 "data: " 前缀
                    if "choices" in json_data and len(json_data["choices"]) > 0:
                        delta = json_data["choices"][0].get("delta", {})
                        if "content" in delta:
                            content_piece = delta["content"]
                            full_response += content_piece
                            current_chunk += content_piece
                            
                            # 当当前块达到一定大小时发送
                            if len(current_chunk) >= chunk_size:
                                chat.SendMsg(current_chunk)
                                current_chunk = ""
                except json.JSONDecodeError:
                    print(f"无法解析JSON: {line}")
                    continue
    
    print('完整ai回答：', full_response)
    return full_response


def deepseek(content):
    """非流式API，保留原有功能"""
    url = "https://api.deepseek.com/v1/chat/completions"
    payload = {
        "model": "deepseek-reasoner",
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

def xq_stream(content, chat):
    """处理服务器发送事件(SSE)流式响应"""
    url = "https://apollo-api-dev.18qjz.cn/apollo/test/ai/chat?message=" + content
    
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    
    try:
        # 使用stream=True参数进行流式请求
        response = requests.get(url, headers=headers, stream=True)
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            chat.SendMsg(f"请求失败，状态码: {response.status_code}")
            return None
            
        # 存储完整回复以便打印日志
        full_response = ""
        # 存储当前片段，当达到一定长度时发送
        current_chunk = ""
        chunk_size = 100  # 每次发送约100个字符
        
        # 用于去重的变量
        last_sent_chunk = ""
        processed_data = set()  # 存储已处理的数据，避免重复处理
        
        # 检查响应是否有iter_lines方法
        if not hasattr(response, 'iter_lines'):
            print("响应对象没有iter_lines方法")
            error_msg = "API响应格式不支持流式处理"
            chat.SendMsg(error_msg)
            return error_msg
        
        # 处理SSE流
        for line in response.iter_lines():
            if not line:
                continue
                
            try:
                line = line.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                # 如果解码失败或line不是bytes类型
                print(f"无法解码行: {type(line)}")
                continue
                
            # SSE格式通常是 "data: {内容}"
            if line.startswith('data:'):
                # 提取data后的内容
                data = line[5:].strip()
                
                # 如果是结束标记则退出
                if data == '[DONE]':
                    # 发送剩余内容
                    if current_chunk and current_chunk != last_sent_chunk:
                        chat.SendMsg(current_chunk)
                        last_sent_chunk = current_chunk
                    break
                
                # 检查是否已经处理过相同的数据
                if data in processed_data:
                    print(f"跳过重复数据: {data[:30]}...")
                    continue
                
                processed_data.add(data)
                    
                try:
                    # 尝试解析JSON (如果API返回JSON格式)
                    json_data = json.loads(data)
                    
                    # 根据实际API响应格式提取内容
                    if isinstance(json_data, dict):
                        if 'content' in json_data:
                            content_piece = json_data['content']
                        elif 'text' in json_data:
                            content_piece = json_data['text']
                        else:
                            # 如果无法确定格式，转为字符串
                            content_piece = str(json_data)
                    else:
                        # 如果不是字典，转为字符串
                        content_piece = str(json_data)
                        
                    # 仅当有新内容时才添加
                    if content_piece:
                        full_response += content_piece
                        current_chunk += content_piece
                    
                    # 当当前块达到一定大小时发送
                    if len(current_chunk) >= chunk_size and current_chunk != last_sent_chunk:
                        chat.SendMsg(current_chunk)
                        last_sent_chunk = current_chunk
                        current_chunk = ""
                        
                except json.JSONDecodeError:
                    # 如果不是JSON格式，直接使用文本
                    content_piece = data
                    # 仅当有新内容时才添加
                    if content_piece:
                        full_response += content_piece
                        current_chunk += content_piece
                    
                    # 当当前块达到一定大小时发送
                    if len(current_chunk) >= chunk_size and current_chunk != last_sent_chunk:
                        chat.SendMsg(current_chunk)
                        last_sent_chunk = current_chunk
                        current_chunk = ""
    except requests.RequestException as e:
        error_msg = f"请求错误: {str(e)}"
        print(error_msg)
        chat.SendMsg(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"处理SSE流时发生错误: {str(e)}"
        print(error_msg)
        # 发送已累积的内容
        if current_chunk and current_chunk != last_sent_chunk:
            chat.SendMsg(current_chunk)
        # 发送错误信息给用户
        chat.SendMsg(f"处理回复时出错: {str(e)}")
        return error_msg
    
    # 确保发送最后的内容块
    if current_chunk and current_chunk != last_sent_chunk:
        chat.SendMsg(current_chunk)
    
    print('完整ai回答：', full_response)
    return full_response


def send_msg(chat, content):
    # 根据需要选择不同的API
    # deepseek_stream(content, chat)  # DeepSeek流式API
    # chat.SendMsg(deepseek(content))  # DeepSeek非流式API
    xq_stream(content, chat)  # 新的SSE流式API


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
