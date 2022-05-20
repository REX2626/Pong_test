from time import perf_counter
import pygame
import os
from objects import Ball, Padel
from menu import Menu
pygame.font.init()

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GamingX Pong")
ICON = pygame.image.load(
    os.path.join('Assets', 'pong_icon.png'))
pygame.display.set_icon(ICON)

SPEED = 230
variable_speed = SPEED
last_collided = None
score_font = pygame.font.SysFont("comicsans", 20)

WHITE = (255, 255, 255)
LIGHT_GREY = (120, 120, 120)
MEDIUM_GREY = (60, 60, 60)
DARK_GREY = (30, 30, 30)
BLACK = (0, 0, 0)

PADEL_WIDTH, PADEL_HEIGHT = 13, 55
RED_PADEL_X = 80
YELLOW_PADEL_X = 820 - PADEL_WIDTH
PADEL_Y = 250 - PADEL_HEIGHT // 2

YELLOW_PADEL_IMAGE = pygame.image.load(
    os.path.join('Assets', 'padel_yellow.png'))
YELLOW_PADEL = pygame.transform.scale(
    YELLOW_PADEL_IMAGE, (PADEL_WIDTH, PADEL_HEIGHT))

RED_PADEL_IMAGE = pygame.image.load(
    os.path.join('Assets', 'padel_red.png'))
RED_PADEL = pygame.transform.scale(
    RED_PADEL_IMAGE, (PADEL_WIDTH, PADEL_HEIGHT))

BACKGROUND_IMAGE = pygame.image.load(
    os.path.join('Assets', 'background.png'))
BACKGROUND = pygame.transform.scale(
    BACKGROUND_IMAGE, (WIDTH, HEIGHT))

BALL_WIDTH, BALL_HEIGHT = 8, 8
BALL_IMAGES = {}
for file in os.listdir(os.fsencode(os.path.join("Assets", "Balls"))):
    BALL_IMAGE = pygame.image.load(
        os.path.join('Assets', 'Balls', os.fsdecode(file)))
    BALL = pygame.transform.scale(
        BALL_IMAGE, (BALL_WIDTH, BALL_HEIGHT))
    BALL_IMAGES[os.fsdecode(file)] = BALL

def get_ball(rally):
    if rally < 5:
        return BALL_IMAGES["ball.png"]
    elif rally < 10:
        return BALL_IMAGES["ball_200.png"]
    elif rally < 15:
        return BALL_IMAGES["ball_150.png"]
    elif rally < 20:
        return BALL_IMAGES["ball_100.png"]
    elif rally < 25:
        return BALL_IMAGES["ball_50.png"]
    else:
        return BALL_IMAGES["ball_0.png"]


def draw_window(yellow: pygame.Rect, red: pygame.Rect, ball: Ball, red_score, yellow_score, rally):
    WIN.fill(BLACK)
    WIN.blit(BACKGROUND, (0, 15))
    pygame.draw.rect(WIN, DARK_GREY, [0, 0, WIDTH, 28])
    WIN.blit(YELLOW_PADEL, (yellow.x, yellow.y))
    WIN.blit(RED_PADEL, (red.x, red.y))
    WIN.blit(get_ball(rally), (ball.x, ball.y))

    red_score_label = score_font.render(f"RED: {red_score}", True, WHITE)
    yellow_score_label = score_font.render(f"YELLOW: {yellow_score}", True, WHITE)
    rally_score_label = score_font.render(f"RALLY: {rally}", True, LIGHT_GREY)

    WIN.blit(red_score_label, (10, 0))
    WIN.blit(yellow_score_label, (WIDTH - yellow_score_label.get_width() - 10, 0))
    WIN.blit(rally_score_label, (WIDTH / 2 - rally_score_label.get_width() / 2, 0))

    pygame.display.update()


def red_handle_movement(keys_pressed, red: Padel):
    red.moving_up = False
    red.moving_down = False
    if keys_pressed[pygame.K_w] and red.y - speed > 38:  # UP
        red.y -= speed
        red.moving_up = True
    if keys_pressed[pygame.K_s] and red.y + speed + red.height < HEIGHT - 10:  # DOWN
        red.y += speed
        red.moving_down = True
    return red


def yellow_handle_movement(keys_pressed, yellow: Padel):
    yellow.moving_up = False
    yellow.moving_down = False
    if keys_pressed[pygame.K_UP] and yellow.y - speed > 38:  # UP
        yellow.y -= speed
        yellow.moving_up = True
    if keys_pressed[pygame.K_DOWN] and yellow.y + speed + yellow.height < HEIGHT - 10:  # DOWN
        yellow.y += speed
        yellow.moving_down = True
    return yellow


def handle_ball_movement(ball: Ball, yellow: Padel, red: Padel):
    global variable_speed
    global last_collided
    event = None
    ball.move(speed, WIDTH // 2)

    if ball.collide_padel(red):
        ball.collision_red(red, spin=last_collided != red)
        if last_collided != red:
            variable_speed *= 1.03
            last_collided = red
            event = "Rally"

    elif ball.collide_padel(yellow):
        ball.collision_yellow(yellow, spin=last_collided != yellow)
        if last_collided != yellow:
            variable_speed *= 1.03
            last_collided = yellow
            event = "Rally"

    ball.boundary_collision(HEIGHT)

    scored = ball.scored(WIDTH)
    if ball.scored(WIDTH):
        ball.restart(WIDTH, HEIGHT)
        variable_speed = SPEED
        event = scored
        last_collided = None
    
    return event


def main():
    global speed
    delta_time = 0

    red_score = 0
    yellow_score = 0
    rally = 0

    red = Padel(RED_PADEL_X, PADEL_Y, PADEL_WIDTH, PADEL_HEIGHT)
    yellow = Padel(YELLOW_PADEL_X, PADEL_Y, PADEL_WIDTH, PADEL_HEIGHT)

    ball = Ball(WIDTH, HEIGHT, BALL_WIDTH, BALL_HEIGHT)

    running = True
    not_paused = True
    while running:
        while not_paused:
            time1 = perf_counter()
            speed = variable_speed * delta_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    not_paused = False
                    running = False
                    pygame.quit()

                elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:
                    not_paused = False

            keys_pressed = pygame.key.get_pressed()
            red = red_handle_movement(keys_pressed, red)
            yellow = yellow_handle_movement(keys_pressed, yellow)

            event = handle_ball_movement(ball, yellow, red)
            if event == "Red":
                red_score += 1
                rally = 0
            elif event == "Yellow":
                yellow_score += 1
                rally = 0
            elif event == "Rally":
                rally += 1

            draw_window(yellow, red, ball, red_score, yellow_score, rally)
            time2 = perf_counter()
            delta_time = time2 - time1
        
        if not running:
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                not_paused = False
                running = False
                pygame.quit()

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:
                not_paused = True


def main_menu():
    menu = Menu(HEIGHT, WIDTH, text_colour=WHITE)
    menu.draw_menu(WIN, background_colour=DARK_GREY, box_colour=MEDIUM_GREY)
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if menu.clicked_on_start(mouse):
                    main()


if __name__ == "__main__":
    main_menu()