import winreg
import win32gui
import win32con
import win32api
from wxauto import WeChat

class DynamicWeChat(WeChat):
    def __init__(self):
        self.class_name = self._get_wechat_class_name()  # 动态获取类名
        super().__init__()

    def _get_wechat_version(self):
        """使用文件版本信息"""
        try:
            # 获取微信安装路径（需从注册表读取）
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat")
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            exe_path = f"{install_path}\\WeChat.exe"
            info = win32api.GetFileVersionInfo(exe_path, '\\')
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        except Exception as e:
            print(f"Version Error: {e}")
            return "3.9.11.17"

    def _get_wechat_class_name(self):
        """根据版本映射窗口类名（需实际验证）"""
        version = self._get_wechat_version()
        parts = list(map(int, version.split('.')))
        # 版本与类名映射表（示例数据需实测）
        class_map = {
            (3, 9): "WeChatlainWndForPC",   # 3.9.x
            (4, 0): "Qt515140WindowIcon" # 4.0.x 测试版
        }
        return class_map.get((parts[0], parts[1]), "WeChatMainWndForPC")

    def find_window(self):
        """重写查找窗口逻辑"""
        try:
            # 核心代码重写
            hwnd = win32gui.FindWindow(self.class_name, "微信")
            if not hwnd:
                hwnd = win32gui.FindWindow(None, "微信")
            return hwnd
        except Exception as e:
            print(f"窗口查找失败: {e}")
            return 0
    #多开支持
    def find_all_wechat_windows(self):
        """查找所有微信窗口句柄"""
        hwnd_list = []
        win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd) if (
            win32gui.GetClassName(hwnd) == self.class_name and 
            win32gui.GetWindowText(hwnd) == "微信"
        ) else None, hwnd_list)
        return hwnd_list

    def connect(self):
        """可选：重写连接方法"""
        #self._hwnd = self.find_window()
        self._hwnd = self.find_all_wechat_windows()
        if self._hwnd:
            self._window = win32gui.GetWindow(self._hwnd, win32con.GW_OWNER)
            return True
        return False