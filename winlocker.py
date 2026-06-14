import pygame
import random
import sys
import time
import webbrowser
import threading
import os

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TEST_TIMER = 15  # секунд для теста (потом заменим на 600)
MUSIC_URL = "https://ost-watch-dogs-2.skysound7.com/t/06067162842068930321-ost-watch-dogs-2-main-menu-theme/"

# === ФУНКЦИЯ ДЛЯ ЗАПУСКА МУЗЫКИ ===
def play_music():
    webbrowser.open(MUSIC_URL)

# === ИНИЦИАЛИЗАЦИЯ Pygame ===
pygame.init()
infoObject = pygame.display.Info()
W, H = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
pygame.display.set_caption("CTOS 2.0")
clock = pygame.time.Clock()
font_big = pygame.font.Font(None, 80)
font_mid = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 30)

# === ЦВЕТА ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_reaper(surf, x, y, frame):
    """Рисует статую Смерти с косой."""
    # Капюшон
    pygame.draw.ellipse(surf, WHITE, (x-20, y-40, 40, 50), 2)
    pygame.draw.polygon(surf, WHITE, [(x-25, y-20), (x, y-40), (x+25, y-20)], 2)
    # Глаза
    if frame % 20 < 10:
        pygame.draw.circle(surf, WHITE, (x-8, y-15), 4)
        pygame.draw.circle(surf, WHITE, (x+8, y-15), 4)
    else:
        pygame.draw.line(surf, WHITE, (x-10, y-15), (x-6, y-15), 2)
        pygame.draw.line(surf, WHITE, (x+6, y-15), (x+10, y-15), 2)
    # Тело
    pygame.draw.line(surf, WHITE, (x, y), (x, y+60), 2)
    # Коса
    angle = frame * 0.05
    end_x = x + int(50 * pygame.math.Vector2(1, 0).rotate(angle)[0])
    end_y = y + int(50 * pygame.math.Vector2(1, 0).rotate(angle)[1])
    pygame.draw.line(surf, WHITE, (x, y-20), (end_x, end_y), 2)

def draw_fake_hack(surf, percent):
    """Рисует фейковую строку загрузки."""
    text = font_mid.render(f"Взлом ctOS 2.0: {percent}%", True, WHITE)
    surf.blit(text, (50, 50))
    bar_width = int((percent / 100) * (W - 200))
    pygame.draw.rect(surf, WHITE, (50, 120, bar_width, 30), 2)
    for i in range(0, bar_width, 15):
        pygame.draw.rect(surf, WHITE, (55 + i, 125, 10, 20))

def fake_facts(surf):
    """Рисует фейковые факты, как в Watch Dogs."""
    facts = [
        "ЗАГРУЗКА ДАННЫХ ПРОФАЙЛА...",
        "СКАНИРОВАНИЕ БИОМЕТРИИ...",
        "ПОДБОР КЛЮЧА ШИФРОВАНИЯ...",
        "ОБХОД ПРОТОКОЛА BLUME...",
        "ДОСТУП К КАМЕРАМ ПОЛУЧЕН...",
        "ВНЕДРЕНИЕ В СЕТЬ ctOS...",
    ]
    y = H - 200
    for fact in facts:
        text = font_small.render(fact, True, WHITE)
        surf.blit(text, (random.randint(50, W//2), y))
        y += 30

# === ЗАПУСК МУЗЫКИ ===
threading.Thread(target=play_music, daemon=True).start()

# === ТАЙМЕР ОЖИДАНИЯ (15 СЕКУНД) ===
start_time = time.time()
while time.time() - start_time < TEST_TIMER:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_F4, pygame.K_TAB, pygame.K_ESCAPE, pygame.K_LALT, pygame.K_RALT, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LSUPER, pygame.K_RSUPER):
                continue
    
    screen.fill(BLACK)
    elapsed = time.time() - start_time
    percent = min(100, int((elapsed / TEST_TIMER) * 100))
    draw_fake_hack(screen, percent)
    
    # Две статуи Смерти по бокам
    draw_reaper(screen, 100, H//2, int(elapsed * 10))
    draw_reaper(screen, W-100, H//2, int(elapsed * 10 + 5))
    
    fake_facts(screen)
    
    # Рисуем летающие частицы (как в Watch Dogs)
    for _ in range(50):
        x = random.randint(0, W)
        y = random.randint(0, H)
        pygame.draw.circle(screen, WHITE, (x, y), 2)
    
    pygame.display.flip()
    clock.tick(30)

# === ОКНО БЛОКИРОВКИ ===
input_box = pygame.Rect(W//2 - 100, H//2 + 50, 200, 40)
text_input = ""

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_F4, pygame.K_TAB, pygame.K_ESCAPE, pygame.K_LALT, pygame.K_RALT, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LSUPER, pygame.K_RSUPER):
                continue
            if event.key == pygame.K_RETURN:
                if text_input == PASSWORD:
                    pygame.quit()
                    sys.exit()
                else:
                    text_input = ""
            elif event.key == pygame.K_BACKSPACE:
                text_input = text_input[:-1]
            else:
                text_input += event.unicode
    
    screen.fill(BLACK)
    
    # Рисуем Смерть, которая ходит вокруг поля ввода
    draw_reaper(screen, W//2, H//2 - 150, int(time.time() * 15) % 30)
    
    prompt = font_mid.render("Введите пароль:", True, WHITE)
    screen.blit(prompt, (W//2 - 150, H//2))
    
    pygame.draw.rect(screen, WHITE, input_box, 2)
    text_surface = font_small.render(text_input, True, WHITE)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 10))
    
    pygame.display.flip()
    clock.tick(30)
