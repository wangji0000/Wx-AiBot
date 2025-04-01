import win32gui
# 获取关于微信相关的句柄
def enum_windows_callback(hwnd, _):
    class_name = win32gui.GetClassName(hwnd)
    title = win32gui.GetWindowText(hwnd)
    if "微信" in title or "WeChat" in title:
        print(f"句柄: {hwnd}, 类名: {class_name}, 标题: {title}")

win32gui.EnumWindows(enum_windows_callback, None)

# 添加以下代码，等待用户输入后再退出
input("按回车键退出...")