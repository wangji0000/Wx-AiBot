import platform
import config_logger
from wxauto import WeChat
import WechatVersion


# ================ 初始化日志记录器 ================
logger = config_logger.setup_logger()

class DynamicWeChat(WeChat):

    def __init__(self):
        self.class_name = self._get_wechat_class_name()  # 动态获取类名
        logger.info("微信句柄: %s", self.class_name)
        super().__init__()

    def _get_wechat_version(self):
        system = platform.system()
        try:
            if system == "Windows":
                return WechatVersion.get_wechat_version_windows()
            elif system == "Darwin":
                return WechatVersion.get_wechat_version_mac()
            else:
                return "不支持的操作系统"
        except Exception as e:
            logger.error(f"Version Error: {e}")
            return "3.9.11.17"

    def _get_wechat_class_name(self):
        """根据版本映射窗口类名（需实际验证）"""
        version = self._get_wechat_version()
        logger.info("当前微信版本号：%s", version)
        parts = list(map(int, version.split('.')))
        # 版本与类名映射表（示例数据需实测）
        class_map = {
            (3, 9): "WeChatMainWndForPC",   # 3.9.x
            (4, 0): "Qt51514QWindowIcon" # 4.0.x 测试版
        }
        return class_map.get((parts[0], parts[1]), "WeChatMainWndForPC")
        