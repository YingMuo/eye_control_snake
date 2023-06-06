import sys
import pygame
import random

# 初始化 Pygame
pygame.init()
pygame.font.init()

# 定義顏色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 設定視窗尺寸
window_width = 800
window_height = 600
window_size = (window_width, window_height)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("貪吃蛇遊戲")

# 定義貪吃蛇初始位置和大小
snake_block_size = 20
snake_speed = 10
snake_list = []
snake_length = 1
snake_head = [window_width / 2, window_height / 2]

# 定義方向
direction = "RIGHT"
change_to = direction

# 定義食物位置
food_block_size = 20
food_pos = [random.randrange(1, (window_width // food_block_size)) * food_block_size,
            random.randrange(1, (window_height // food_block_size)) * food_block_size]

# 定義分數
score = 0

def gamesetting_init():
    global snake_head, snake_length, snake_list
    snake_list = []
    snake_length = 1
    snake_head = [window_width / 2, window_height / 2]

    global direction, change_to
    direction = "RIGHT"
    change_to = direction

    global running, show_init, show_over
    running = True
    show_init = True
    show_over = False

    global food_pos
    food_pos = [random.randrange(1, (window_width // food_block_size)) * food_block_size,
            random.randrange(1, (window_height // food_block_size)) * food_block_size]
    return

def game_init():
    start_font = pygame.font.Font(None, 50)
    instructions_font = pygame.font.Font(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        screen.fill(BLACK)
        start_text = start_font.render("Snake", True, WHITE)
        start_text_rect = start_text.get_rect(center=(window_width // 2, window_height // 2 - 50))

        instructions_text = instructions_font.render("Press Enter to Start", True, WHITE)
        instructions_text_rect = instructions_text.get_rect(center=(window_width // 2, window_height // 2 + 50))

        screen.blit(start_text, start_text_rect)
        screen.blit(instructions_text, instructions_text_rect)
        pygame.display.flip()

def game_over():
    #顯示結束畫面
    game_over_font = pygame.font.Font(None, 50)
    game_over_text = game_over_font.render("Game Over!", True, RED)
    game_over_text_rect = game_over_text.get_rect(center=(window_width // 2, window_height // 2 -30))
    score_font = pygame.font.Font(None, 35)
    score_text = score_font.render("Score: " + str(score), True, WHITE)
    score_text_rect = score_text.get_rect(center=(window_width // 2, window_height // 2 ))
    back_init_font = pygame.font.Font(None, 30)
    back_init_font_text = back_init_font.render("Press Enter to Restart", True, WHITE)
    back_init_font_text_rect = back_init_font_text.get_rect(center=(window_width // 2, window_height // 2 +30))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

        screen.fill(BLACK)
        screen.blit(game_over_text, game_over_text_rect)
        screen.blit(score_text, score_text_rect)
        screen.blit(back_init_font_text, back_init_font_text_rect)
        pygame.display.flip()

def draw_snake(snake_block_size, snake_list):
    # 繪製貪吃蛇
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block_size, snake_block_size])

def draw_food(food_block_size, food_pos):
    # 繪製食物
    pygame.draw.rect(screen, RED, [food_pos[0], food_pos[1], food_block_size, food_block_size])


# 遊戲迴圈
running = True
show_init = True
show_over = False
clock = pygame.time.Clock()

while running:
    if show_init:
        game_init()
        show_init = False

    clock.tick(snake_speed)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
    # 使用自訂義方式更改方向
    # change_to = get_eye_dir()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and direction != "RIGHT":
                change_to = "LEFT"
            elif event.key == pygame.K_RIGHT and direction != "LEFT":
                change_to = "RIGHT"
            elif event.key == pygame.K_UP and direction != "DOWN":
                change_to = "UP"
            elif event.key == pygame.K_DOWN and direction != "UP":
                change_to = "DOWN"

    # 更新貪吃蛇的方向
    if change_to == "LEFT" and direction != "RIGHT":
        direction = "LEFT"
    elif change_to == "RIGHT" and direction != "LEFT":
        direction = "RIGHT"
    elif change_to == "UP" and direction != "DOWN":
        direction = "UP"
    elif change_to == "DOWN" and direction != "UP":
        direction = "DOWN"

    # 根據方向更新貪吃蛇的位置
    if direction == "LEFT":
        snake_head[0] -= snake_block_size
    elif direction == "RIGHT":
        snake_head[0] += snake_block_size
    elif direction == "UP":
        snake_head[1] -= snake_block_size
    elif direction == "DOWN":
        snake_head[1] += snake_block_size

    # 更新貪吃蛇的位置
    snake_list.append(list(snake_head))
    if len(snake_list) > snake_length:
        del snake_list[0]

    # 碰撞檢測
    for x in snake_list[:-1]:
        if x == snake_head:
            show_over = True

    if snake_head[0] < 0 or snake_head[0] >= window_width or snake_head[1] < 0 or snake_head[1] >= window_height:
        show_over = True

    # 檢測是否吃到食物
    if snake_head[0] == food_pos[0] and snake_head[1] == food_pos[1]:
        score += 1
        snake_length += 1
        food_pos = [random.randrange(1, (window_width // food_block_size)) * food_block_size,
                    random.randrange(1, (window_height // food_block_size)) * food_block_size]

    # 遊戲結束
    if show_over:
        game_over()
        gamesetting_init()
        
    # 清空視窗
    screen.fill(BLACK)
    # 繪製貪吃蛇和食物
    draw_snake(snake_block_size, snake_list)
    draw_food(food_block_size, food_pos)
    # 更新視窗
    pygame.display.update()

pygame.quit()