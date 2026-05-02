import pygame
import sys
import random
import math

pygame.init()

# -------------------- НАСТРОЙКИ --------------------
WIDTH, HEIGHT = 900, 520
FPS = 60
WIN_SCORE = 10

BG = (14, 16, 24)
PANEL = (22, 26, 38)
WHITE = (245, 247, 255)
MUTED = (160, 168, 190)
ACCENT = (92, 225, 230)
ACCENT2 = (255, 92, 138)
SHADOW = (5, 7, 12)
LINE = (75, 82, 110)

PADDLE_W, PADDLE_H = 14, 100
BALL_SIZE = 16

PADDLE_SPEED = 7
BALL_START_SPEED = 6
BALL_MAX_SPEED = 12
SPEEDUP = 1.04

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping-Pong Deluxe")
clock = pygame.time.Clock()

FONT_BIG = pygame.font.SysFont("arial", 56, bold=True)
FONT_MID = pygame.font.SysFont("arial", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20)

# -------------------- ОБЪЕКТЫ --------------------
left_paddle = pygame.Rect(35, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
right_paddle = pygame.Rect(WIDTH - 35 - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

ball_dx = BALL_START_SPEED * random.choice((-1, 1))
ball_dy = random.choice([-4, -3, 3, 4])

left_score = 0
right_score = 0
winner = None
game_started = False

# -------------------- ФУНКЦИИ --------------------
def reset_ball(direction=None):
    global ball_dx, ball_dy
    ball.center = (WIDTH // 2, HEIGHT // 2)

    if direction is None:
        direction = random.choice((-1, 1))

    ball_dx = BALL_START_SPEED * direction
    ball_dy = random.choice([-4, -3, 3, 4])

def reset_game():
    global left_score, right_score, winner, game_started
    left_score = 0
    right_score = 0
    winner = None
    game_started = False
    left_paddle.y = HEIGHT // 2 - PADDLE_H // 2
    right_paddle.y = HEIGHT // 2 - PADDLE_H // 2
    reset_ball()

def draw_text(text, font, color, x, y, center=True):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

def draw_background():
    screen.fill(BG)
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 72))
    pygame.draw.line(screen, LINE, (0, 72), (WIDTH, 72), 2)

    for y in range(90, HEIGHT, 28):
        pygame.draw.rect(screen, LINE, (WIDTH // 2 - 2, y, 4, 16))

    pygame.draw.rect(screen, (35, 40, 58), (16, 88, WIDTH - 32, HEIGHT - 104), 2)

def draw_paddle(rect, color):
    shadow_rect = rect.move(4, 5)
    pygame.draw.rect(screen, SHADOW, shadow_rect)
    pygame.draw.rect(screen, color, rect)

def draw_ball(rect):
    shadow = rect.move(4, 5)
    pygame.draw.ellipse(screen, SHADOW, shadow)
    pygame.draw.ellipse(screen, WHITE, rect)
    inner = rect.inflate(-8, -8)
    pygame.draw.ellipse(screen, ACCENT, inner, 2)

def paddle_collision(paddle, is_left):
    global ball_dx, ball_dy

    if not ball.colliderect(paddle):
        return

    if is_left and ball_dx < 0:
        ball.left = paddle.right
    elif not is_left and ball_dx > 0:
        ball.right = paddle.left
    else:
        return

    paddle_center = paddle.centery
    hit_pos = (ball.centery - paddle_center) / (PADDLE_H / 2)
    ball_dy = int(hit_pos * 7)

    if ball_dy == 0:
        ball_dy = random.choice([-2, 2])

    ball_dx *= -SPEEDUP
    ball_dy *= 1.02

    speed = math.hypot(ball_dx, ball_dy)
    if speed > BALL_MAX_SPEED:
        scale = BALL_MAX_SPEED / speed
        ball_dx *= scale
        ball_dy *= scale

def update_ball():
    global left_score, right_score, winner

    ball.x += int(ball_dx)
    ball.y += int(ball_dy)

    if ball.top <= 88:
        ball.top = 88
        globals()["ball_dy"] *= -1
    if ball.bottom >= HEIGHT - 16:
        ball.bottom = HEIGHT - 16
        globals()["ball_dy"] *= -1

    paddle_collision(left_paddle, True)
    paddle_collision(right_paddle, False)

    if ball.right < 0:
        right_score += 1
        if right_score >= WIN_SCORE:
            winner = "Правый игрок победил!"
        else:
            reset_ball(direction=1)

    if ball.left > WIDTH:
        left_score += 1
        if left_score >= WIN_SCORE:
            winner = "Левый игрок победил!"
        else:
            reset_ball(direction=-1)

def draw_hud():
    score_text = FONT_MID.render(f"{left_score}    {right_score}", True, WHITE)
    score_shadow = FONT_MID.render(f"{left_score}    {right_score}", True, SHADOW)
    screen.blit(score_shadow, score_text.get_rect(center=(WIDTH // 2 + 3, 36 + 3)))
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 36)))

    draw_text("PING-PONG", FONT_MID, ACCENT, 30, 22, center=False)
    draw_text("W/S", FONT_SMALL, MUTED, 30, HEIGHT - 34, center=False)
    draw_text("↑ / ↓", FONT_SMALL, MUTED, WIDTH - 90, HEIGHT - 34, center=False)

def draw_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

# -------------------- ЦИКЛ --------------------
reset_ball()

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_SPACE and winner is None:
                game_started = True

    keys = pygame.key.get_pressed()

    if winner is None and game_started:
        if keys[pygame.K_w]:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s]:
            left_paddle.y += PADDLE_SPEED
        if keys[pygame.K_UP]:
            right_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN]:
            right_paddle.y += PADDLE_SPEED

        left_paddle.y = max(88, min(HEIGHT - 16 - PADDLE_H, left_paddle.y))
        right_paddle.y = max(88, min(HEIGHT - 16 - PADDLE_H, right_paddle.y))

        update_ball()

    draw_background()
    draw_paddle(left_paddle, ACCENT)
    draw_paddle(right_paddle, ACCENT2)
    draw_ball(ball)
    draw_hud()

    if not game_started and winner is None:
        draw_overlay()
        draw_text("Нажми SPACE, чтобы начать", FONT_BIG, WHITE, WIDTH // 2, HEIGHT // 2 - 40)
        draw_text("W/S и ↑/↓ для управления", FONT_MID, MUTED, WIDTH // 2, HEIGHT // 2 + 18)
        draw_text("R — полный рестарт", FONT_SMALL, MUTED, WIDTH // 2, HEIGHT // 2 + 58)

    if winner is not None:
        draw_overlay()
        draw_text(winner, FONT_BIG, WHITE, WIDTH // 2, HEIGHT // 2 - 40)
        draw_text("Нажми R, чтобы сыграть снова", FONT_MID, MUTED, WIDTH // 2, HEIGHT // 2 + 18)

    pygame.display.flip()

pygame.quit()
sys.exit()