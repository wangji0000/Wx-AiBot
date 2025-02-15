# DeepSeek 微信智能聊天机器人

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub stars](https://img.shields.io/github/stars/yourusername/deepseek-wechat-bot?style=social)

将 DeepSeek 大模型接入微信，实现智能聊天机器人。通过监听微信消息，调用 DeepSeek API 生成回复，并自动发送给好友或群聊。

## 功能特性

- **智能回复**: 基于 DeepSeek 大模型，实现自然语言对话。
- **多用户支持**: 支持监听多个微信好友或群聊。
- **较为稳定**: 采用监控窗口采集信息，自动化发送，比传统itchat更为安全。
- **易于部署**: 简单配置即可运行。

## 快速开始

### 1. 环境准备

- Python 3.8+
- 微信客户端（**请先登录这个版本！！！***，版本3.9.11.17）[点击下载](https://github.com/tom-snow/wechat-windows-versions/releases/download/v3.9.11.17/WeChatSetup-3.9.11.17.exe)
- DeepSeek API Key（[API链接](https://cloud.siliconflow.cn/models)）

### 2. 克隆项目

```bash
git clone https://github.com/2423560192/Wx-AiBot.git
cd Wx-AiBot
```

### 3\. 安装依赖

 
```
pip install -r requirements.txt
```
 
### 4\. 配置
 
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
 
### 5\. 运行项目
 

 

 
```
python app.py
```
 
### 6\. 使用说明
 
*   程序启动后，会自动监听 `users.txt` 中指定的好友或群聊消息。（请提前将好友页打开，避免检测不到窗口）
    
*   当收到消息时，程序会调用 DeepSeek API 生成回复，并自动发送。
    
*   聊天记录会保存到 `db.json` 文件中。
    
 
项目结构
----

 
```
deepseek-wechat-bot/
├── app.py                  # 主程序
├── config.ini              # 配置文件
├── users.txt               # 监听用户列表
├── requirements.txt        # 依赖文件
├── README.md               # 项目说明
└── LICENSE                 # 开源协议
```
 
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
    
 
开源协议
----
 
本项目基于 [MIT License](https://chat.deepseek.com/a/chat/s/LICENSE) 开源。
 

    
 
联系作者
----
 
如有问题或建议，请联系：
 
*   邮箱: 2480419172@qq.com
    
*   GitHub: [小廉](https://github.com/2423560192)
    
 
* * *
 
 
免责声明
----
 
本项目仅供学习和研究使用，请勿用于商业或非法用途。使用本项目产生的任何后果，作者概不负责。
 
### 重要提示
 
1.  **微信使用规范**:  
    使用本项目时，请遵守微信的使用规范和法律法规。任何滥用微信 API 或自动化工具的行为可能导致微信账号被封禁，作者不承担任何责任。
    
2.  **API 调用限制**:  
    DeepSeek API 可能有调用频率限制或收费政策，请确保在使用前了解相关规则，避免产生额外费用或服务中断。
    
3.  **数据隐私**:  
    本项目会监听微信消息并调用第三方 API，请确保你已获得相关聊天参与者的同意。作者不对因数据泄露或滥用导致的任何问题负责。
    
4.  **风险自担**:  
    本项目为开源项目，作者不对其稳定性、安全性或适用性作任何保证。使用者需自行承担一切风险。
    
5.  **禁止滥用**:  
    禁止将本项目用于任何形式的骚扰、欺诈、垃圾信息发送等非法或不道德行为。如有违反，责任自负。
    
 
### 法律声明
 
本项目遵循 [MIT License](https://chat.deepseek.com/a/chat/s/LICENSE)，作者不对使用者因使用本项目而产生的任何直接或间接损失负责。使用者一旦使用本项目，即视为已阅读并同意本免责声明的全部内容。
