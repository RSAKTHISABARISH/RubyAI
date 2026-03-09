import win32gui

def callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            windows.append(title)
    return True

windows = []
win32gui.EnumWindows(callback, windows)
print("\n".join(list(set(windows))))
