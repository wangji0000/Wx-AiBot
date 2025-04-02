import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# ================ 日志配置核心部分 ================
def setup_logger():
    """配置全局日志记录器（按天轮转）"""

    # 1. 动态生成日志目录（兼容开发环境和打包后的exe）
    if getattr(sys, 'frozen', False):
        # 打包后.exe所在目录
        base_dir = Path(sys.executable).parent
    else:
        # 开发环境脚本所在目录
        base_dir = Path(__file__).parent

    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)  # 自动创建目录

    # 2. 定义日志文件名格式（带日期轮转）
    log_file = log_dir / "AiBot.log"

    # 3. 创建主日志记录器（记录全量DEBUG及以上级别）
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # 捕获所有级别日志

    # 4. 定义日志格式
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 5. 按天轮转的文件处理器（关键配置）
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",     # 每天午夜轮转
        interval=1,          # 每天一个文件
        backupCount=7,       # 保留最近7天日志
        encoding="utf-8",
        utc=False            # 使用本地时间轮转
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)  # 文件记录全量日志

    # 6. 控制台输出（可选，INFO级别以上）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # 控制台只显示INFO及以上

    # 7. 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# ================== 2. 全局异常捕获 ==================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """全局异常处理函数"""
    if issubclass(exc_type, KeyboardInterrupt):
        # 保留默认的Ctrl+C退出行为
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # 获取主日志记录器
    logger = logging.getLogger("MyApp")
    logger.critical(
        "未捕获的全局异常",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

# 覆盖系统异常钩子
sys.excepthook = global_exception_handler