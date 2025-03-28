# DeepSeek 微信智能聊天机器人

将 DeepSeek 大模型接入微信，实现智能聊天机器人。通过监听微信消息，调用 DeepSeek API 生成回复，并自动发送给好友或群聊。

## 功能特性

- **智能回复**: 基于 DeepSeek 大模型，实现自然语言对话。
- **多用户支持**: 支持监听多个微信好友或群聊。
- **较为稳定**: 采用监控窗口采集信息，自动化发送，比传统itchat更为安全。
- **易于部署**: 简单配置即可运行。

## 快速开始

### 1. 环境准备

- Python 3.8+
- 微信客户端（版本3.9.11.17）


### 2\. 安装依赖

 
```
python -m pip install -r requirements.txt
```
 
### 3\. 配置
 
1.  在项目根目录下打开 `config.ini` 文件，填写 DeepSeek API Key：
    ```
    [API]
    key = 12312313
    ```
2.  在 `users.txt` 文件中添加需要监听的好友或群聊名称，每行一个名称：
    
    ```
    好友A
    群聊B
    ```
    
 
### 4\. 运行项目
 

 

 
```
python AiBot.py
```
 
### 5\. 使用说明
 
*   程序启动后，会自动监听 `users.txt` 中指定的好友或群聊消息。（请提前将好友页打开，避免检测不到窗口）
    
*   当收到消息时，程序会调用 DeepSeek API 生成回复，并自动发送。
    
 
配置选项
----
 
### `config.ini`
 
*   `key`: DeepSeek API Key，必填。
    
 
### `users.txt`
 
*   每行一个微信好友或群聊名称，程序会监听这些聊天窗口的消息。
    
 
依赖库
---
 
*   `wxauto`: 微信自动化工具，用于监听和发送消息。
    
*   `requests`: 用于发送 HTTP 请求，调用 DeepSeek API。
    
*   `configparser`: 打开配置文件。


打包
安装 PyInstaller 如果你还没有安装：  python -m  pip install PyInstaller

打包命令（基本版本）：  python -m PyInstaller --onefile --icon=assets/AiBot.ico --add-data "users.txt;." --add-data "conf.ini;." AiBot.py 

# 清理旧构建文件

window系统: Remove-Item -Recurse -Force build, dist

Unix/Linux系统:  rm -rf build dist
