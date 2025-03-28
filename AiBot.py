import configparser
import os
import requests
import json
import sys
from wxauto import WeChat

def get_resource_path(relative_path):
    """ 获取资源的绝对路径 """
    if getattr(sys, 'frozen', False):
        # 打包后，sys.executable是EXE路径
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发时，使用当前文件路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 读取users.txt
users_path = get_resource_path("users.txt")
if not os.path.exists(users_path):
    with open(users_path, "w", encoding='utf-8') as f:
        f.write(" ") 

with open(users_path, "r", encoding='utf-8') as f:
    users = f.read().splitlines()

# 获取配置文件
config_path = get_resource_path('conf.ini')
config = configparser.ConfigParser()
if not os.path.exists(config_path):
    if not os.path.exists(config_path):
        config["DEFAULT"] = {
            "debug_mode": False,
            "max_connections": "10",
            "log_path": "logs/AiBot.log"
        }
        config["API"] = {
            "baseUrl": "https://api.deepseek.com",
            "key": "sk-003d5efa9dd14ef382d8a238b7341107",
            "model": "deepseek-reasoner",
            "max_tokens": "512",
            "temperature": "0.7",
            "top_k": "5",
            "frequency_penalty": "0.5"
        }
        config["INTERFACEAPI"] = {
            "baseUrl": "https://apollo-api-dev.18qjz.cn",
            "type": "1",
        }
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)

with open(config_path, "r", encoding='utf-8') as f:
    config.read(config_path, encoding="utf-8")
    
# 读取users.txt加载监听用户
def load_monitor_list():
    """加载监听用户列表，允许动态更新"""
    monitor_list = []
    users_path = 'users.txt'  # 使用相对路径，保持在exe同目录
    if not os.path.exists(users_path):
        fp = open(users_path, encoding="utf-8", mode='w')
        fp.close()
    else:
        fp = open(users_path, encoding="utf-8", mode='r')
        for line in fp:
            line = line.strip()
            if not line:
                continue
            monitor_list.append(line)
        fp.close()
    return monitor_list

def load_config():
    """ 动态加载配置文件（支持热更新） """
    config_path = get_resource_path("conf.ini")
    # 读取最新配置
    config.read(config_path, encoding="utf-8")
    return config

# 全局配置对象（需定期调用 reload_config() 刷新）
config = load_config()

# 初始化监听列表
MONITOR_LIST = load_monitor_list()

# 1.打开微信
wx = WeChat()

# 2.监听账户列表（好友名称）
def update_listen_chats():
    """更新监听的聊天列表"""
    # 重新创建 WeChat 实例，确保完全重置监听状态
    global wx
    wx = WeChat()
    
    # 重新加载监听列表
    global MONITOR_LIST
    MONITOR_LIST = load_monitor_list()
    
    # 添加监听
    for ele in MONITOR_LIST:
        wx.AddListenChat(who=ele, savepic=True)
    print("已更新监听用户列表")

# 初始化监听
update_listen_chats()


def reload_config():
    global config
    config = load_config()
    print("配置已刷新")


# 刷新监听列表的函数（可以定期调用）
def refresh_monitor_list():
    """刷新监听列表，用于动态更新配置"""
    update_listen_chats()
    reload_config()

# 3.监听消息
def deepseek_stream(content, chat):
    """使用流式API获取DeepSeek响应并发送消息"""
    base_url = config['API']['baseUrl']
    url = f"{base_url}/v1/chat/completions"
    payload = {
        "model": config['API']['model'],
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": True,
        "max_tokens": int(config['API']['max_tokens']),
        "temperature": float(config['API']['temperature']),
        "top_k": int(config['API']['top_k']),
        "frequency_penalty": float(config['API']['frequency_penalty']),
        "response_format": {"type": "text"},
    }
    headers = {
        "Authorization": f"Bearer {config['API']['key']}",
        "Content-Type": "application/json"
    }

    # 使用stream=True参数进行流式请求
    try:
        response = requests.request("POST", url, json=payload, headers=headers, stream=True)
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            chat.SendMsg(f"请求失败，状态码: {response.status_code}")
            return None

        # 存储完整回复以便打印日志
        full_response = ""
        # 存储当前片段，当达到一定长度时发送
        current_chunk = ""
        chunk_size = 200  # 每次发送约200个字符
        
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
                                if content_piece is not None:
                                    full_response += content_piece
                                    current_chunk += content_piece
                                
                                # 当当前块达到一定大小时发送
                                if len(current_chunk) >= chunk_size:
                                    chat.SendMsg(current_chunk)
                                    current_chunk = ""
                    except json.JSONDecodeError:
                        print(f"无法解析JSON: {line}")
                        continue
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
    
    print('deepseek智能AI流式回答：', full_response)
    return full_response


def deepseek(content):
    """非流式API，保留原有功能"""
    base_url = config['API']['baseUrl']
    url = f"{base_url}/v1/chat/completions"

    payload = {
        "model": config['API']['model'],
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "stream": False,
        "max_tokens": int(config['API']['max_tokens']),
        "temperature": float(config['API']['temperature']),
        "top_k": int(config['API']['top_k']),
        "frequency_penalty": float(config['API']['frequency_penalty']),
        "response_format": {"type": "text"}
    }

    headers = {
        "Authorization": f"Bearer {config['API']['key']}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.request("POST", url, json=payload, headers=headers)
        response.raise_for_status()  # 检查HTTP状态码
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP错误: {e}\n响应内容: {response.text}"
        print(error_msg)
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"请求失败: {e}"
        print(error_msg)
        return error_msg

    try:
        data = response.json()
        content = data['choices'][0]['message']['content']
        print('deepseek智能AI回答：', content)
        return content
    except json.JSONDecodeError:
        error_msg = f"JSON解析失败！原始响应内容：\n{response.text}"
        print(error_msg)
        return error_msg
    except KeyError:
        error_msg = f"响应格式异常！原始数据：\n{data}"
        print(error_msg)
        return error_msg

def xq_stream(content, chat):
    """处理服务器发送事件(SSE)流式响应"""
    base_url = config['INTERFACEAPI']['baseUrl']
    url = f"{base_url}/apollo/test/ai/chat?message={content}"

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
        chunk_size = 200  # 每次发送约200个字符
        
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
    
    print('新腔科技智能AI回答：', full_response)
    return full_response


def send_msg(chat, content, type):   
    if type == 2:
        deepseek_stream(content, chat)  # DeepSeek流式API
    elif type == 3:
        chat.SendMsg(deepseek(content))  # DeepSeek非流式API
    else:
        xq_stream(content, chat) # 新的SSE流式API    


def listen_and_reply():
    # 监听消息前先刷新一次配置
    refresh_monitor_list()
    while True:
        msgs = wx.GetListenMessage()
        for chat in msgs:
            one_msgs = msgs.get(chat)
            for msg in one_msgs:
                if msg.type == 'time' or msg.type == 'self' or msg.type == 'sys':
                    continue
                print(msg)
                content = msg.content

                # 特殊命令：刷新配置
                if content.strip() == "刷新配置":
                    refresh_monitor_list()
                    print("已刷新监听用户列表")
                    continue

                # 发送消息
                send_msg(chat, content, int(config['INTERFACEAPI']['type']))
                
listen_and_reply()
