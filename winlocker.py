import pygame
import random
import sys
import time

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TEST_TIMER = 15  # секунд для теста (потом заменим на 600)

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
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# === ГЛОБАЛЬНАЯ ПЕРЕМЕННАЯ ДЛЯ БЛОКИРОВКИ КЛАВИШ ===
block_keys = True

def draw_skull(surf, x, y, laugh_frame=0):
    """Рисует череп, который меняется (смеётся) в зависимости от кадра."""
    # Голова
    pygame.draw.ellipse(surf, WHITE, (x-40, y-30, 80, 60), 2)
    # Глаза
    eye_h = 20 + (5 if laugh_frame % 10 < 5 else -5)
    pygame.draw.circle(surf, WHITE, (x-20, y-10), 15)
    pygame.draw.circle(surf, WHITE, (x+20, y-10), 15)
    # Зрачки
    pygame.draw.circle(surf, BLACK, (x-20, y-10), 8)
    pygame.draw.circle(surf, BLACK, (x+20, y-10), 8)
    # Нос
    pygame.draw.polygon(surf, WHITE, [(x-10, y+20), (x+10, y+20), (x, y+30)])
    # Рот (меняется при смехе)
    if laugh_frame % 10 < 5:
        pygame.draw.arc(surf, WHITE, (x-30, y+10, 60, 40), 3.14, 0, 3)
    else:
        pygame.draw.rect(surf, WHITE, (x-30, y+25, 60, 20))
    # Зубы
    for i in range(4):
        pygame.draw.line(surf, WHITE, (x-15 + i*10, y+30), (x-15 + i*10, y+40), 1)

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

# === ТАЙМЕР ОЖИДАНИЯ (15 СЕКУНД) ===
start_time = time.time()
while time.time() - start_time < TEST_TIMER:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass  # Игнорируем попытки закрыть окно
        if event.type == pygame.KEYDOWN:
            # Блокируем Alt+F4, Alt+Tab, Ctrl+Shift+Esc, Win и другие
            if event.key in (pygame.K_F4, pygame.K_TAB, pygame.K_ESCAPE, pygame.K_LALT, pygame.K_RALT, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LSUPER, pygame.K_RSUPER):
                continue  # Просто игнорируем эти клавиши
    
    screen.fill(BLACK)
    elapsed = time.time() - start_time
    percent = min(100, int((elapsed / TEST_TIMER) * 100))
    draw_fake_hack(screen, percent)
    
    # Рисуем несколько черепов по всему экрану
    for i in range(5):
        x = random.randint(100, W-100)
        y = random.randint(150, H-150)
        draw_skull(screen, x, y, int(elapsed * 10 + i))
    
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
            pass  # Игнорируем попытки закрыть окно
        if event.type == pygame.KEYDOWN:
            # Блокируем Alt+F4, Alt+Tab, Ctrl+Shift+Esc, Win и другие
            if event.key in (pygame.K_F4, pygame.K_TAB, pygame.K_ESCAPE, pygame.K_LALT, pygame.K_RALT, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LSUPER, pygame.K_RSUPER):
                continue  # Просто игнорируем эти клавиши
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
    draw_skull(screen, W//2, H//2 - 100, int(time.time() * 10) % 20)
    
    prompt = font_mid.render("Введите пароль:", True, WHITE)
    screen.blit(prompt, (W//2 - 150, H//2))
    
    pygame.draw.rect(screen, WHITE, input_box, 2)
    text_surface = font_small.render(text_input, True, WHITE)
    screen.blit(text_surface, (input_box.x + 5, input_box.y + 10))
    
    pygame.display.flip()
    clock.tick(30)
