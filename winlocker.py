import tkinter as tk
import os, sys, time

PASSWORD = "1601"
MAX_ATTEMPTS = 4
attempts_left = MAX_ATTEMPTS

class WinLocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.configure(bg='#1a3a5c')
        self.win.overrideredirect(True)
        
        tk.Label(self.win, text="ENTER PASSWORD:", bg='#1a3a5c', fg='white', font=('Arial', 20)).pack(pady=20)
        self.pw = tk.Entry(self.win, show="*", font=('Arial', 20))
        self.pw.pack()
        self.sl = tk.Label(self.win, text=f"ATTEMPTS: {attempts_left}", bg='#1a3a5c', fg='white')
        self.sl.pack()
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            self.sl.config(text="OK!")
            self.win.after(1000, lambda: os._exit(0))
        else:
            attempts_left -= 1
            self.sl.config(text=f"WRONG! LEFT: {attempts_left}")
            if attempts_left <= 0:
                self.sl.config(text="BYE!")
                self.win.after(1000, lambda: os._exit(0))

if __name__ == "__main__":
    WinLocker()
    tk.mainloop()
