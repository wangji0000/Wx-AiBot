import winreg
import plistlib
import subprocess
import os
import win32api

def get_wechat_version_windows():
    """使用文件版本信息"""
    install_path = None
    try:
        # 尝试从多个注册表路径获取安装路径
        reg_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat"),
            (winreg.HKEY_CURRENT_USER, r"Software\Tencent\Weixin"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tencent\WeChat"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\WeChat"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tencent\Weixin"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\Weixin")
        ]
        for hive, path in reg_paths:
            try:
                key = winreg.OpenKey(hive, path)
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                break
            except FileNotFoundError:
                continue
        if not install_path:
            return "3.9.11.17"
        
        exe_path = os.path.join(install_path, "WeChat.exe")
        if not os.path.isfile(exe_path):
            exe_path = os.path.join(install_path, "Weixin.exe")
            if not os.path.isfile(exe_path):
                return "3.9.11.17"
        
        info = win32api.GetFileVersionInfo(exe_path, '\\')
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
    except Exception as e:
        return "3.9.11.17"
    
def get_wechat_version_mac():
    try:
        plist_path = "/Applications/WeChat.app/Contents/Info.plist"
        with open(plist_path, "rb") as f:
            plist_data = plistlib.load(f)
        return plist_data["CFBundleShortVersionString"]
    except FileNotFoundError:
        # 尝试通过mdfind查找路径
        try:
            result = subprocess.run(
                ["mdfind", "kMDItemCFBundleIdentifier == 'com.tencent.xinWeChat'"],
                capture_output=True,
                text=True
            )
            path = result.stdout.strip()
            if not path:
                return "微信未安装"
            
            plist_path = f"{path}/Contents/Info.plist"
            with open(plist_path, "rb") as f:
                plist_data = plistlib.load(f)
            return plist_data["CFBundleShortVersionString"]
        except Exception as e:
            return f"查找失败: {str(e)}"
    except Exception as e:
        return f"读取失败: {str(e)}"    