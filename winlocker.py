import tkinter as tk
import os

PASSWORD = "1601"
MAX_ATTEMPTS = 4
attempts_left = MAX_ATTEMPTS

class WinLocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.configure(bg='black')
        self.win.overrideredirect(True)
        
        msg = f"""Ну привет друг, как у тебя дела?

Да, понимаю, ты попался.
Ну и нахуя ты скачал игру из инета?
Я не пойму...

Ну ладно, вот тебе загадка. Там пароль.

Я — год, когда произошло событие,
которое не произошло.
В Англии заговорщики планировали
взорвать парламент и убить короля.
Их план провалился, король выжил,
а заговорщиков казнили.
Но в Windows я стал началом времён.

ЧТО Я ЗА ЧИСЛО?

У ТЕБЯ {MAX_ATTEMPTS} ПОПЫТКИ."""
        
        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier',9,'bold'), justify='left').place(relx=0.5, rely=0.4, anchor='center')
        
        tk.Label(self.win, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier',14,'bold')).place(relx=0.5, rely=0.8, anchor='center')
        
        self.pw = tk.Entry(self.win, show="*", font=('Courier',14,'bold'), bg='white', fg='black')
        self.pw.place(relx=0.5, rely=0.85, anchor='center', width=200, height=35)
        
        self.sl = tk.Label(self.win, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier',12,'bold'))
        self.sl.place(relx=0.5, rely=0.9, anchor='center')
        
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            self.sl.config(text="ВЕРНО!")
            self.win.after(1000, lambda: os._exit(0))
        else:
            attempts_left -= 1
            if attempts_left > 0:
                self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}")
            else:
                self.sl.config(text="404 | ОШИБКА")
                self.win.after(2000, lambda: os._exit(0))
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    WinLocker()
    tk.mainloop()
