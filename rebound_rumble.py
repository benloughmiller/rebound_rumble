import pygame
import sys
import math
import random
from main_menu import draw_menu, handle_menu_input
from pause_menu import draw_pause_menu, handle_pause_input
from game_over import draw_game_over_screen
from game_states import MENU, PLAYING, PAUSED, GAME_OVER

pygame.init()

#Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
PADDLE_SPEED = 6 #Speed of the paddle
BALL_BASE_SPEED = 2 #Base speed for the ball
BALL_SPEED_INCREMENT = 1.15 #Speed Increase Per Hit
BALL_MAX_SPEED = 10 #Caps the ball speed
BLOCK_SIZE = 40 #Size of the corner blocks

#Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)

#Sounds
hit_sound = pygame.mixer.Sound("audio/hit_paddle.wav")
score_sound = pygame.mixer.Sound("audio/sound_goal.wav")

#Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rebound Rumble")

#Game Clock
clock = pygame.time.Clock()

#Ball position and velocity
ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
ball_dx, ball_dy = BALL_BASE_SPEED, BALL_BASE_SPEED

#Paddle Objects
paddles = [
    pygame.Rect(20, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT),  # Left paddle
    pygame.Rect(SCREEN_WIDTH - 20 - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT),  # Right paddle
    pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_HEIGHT // 2, SCREEN_HEIGHT - 20 - PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_WIDTH), #Bottom paddle
    pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_HEIGHT // 2, 20, PADDLE_HEIGHT, PADDLE_WIDTH), #Top paddle
]

#Ball Object
ball = pygame.Rect(ball_x, ball_y, BALL_SIZE, BALL_SIZE)

#Corner Block Objects
blocks = [
    pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE), #Top-left
    pygame.Rect(SCREEN_WIDTH - BLOCK_SIZE, 0, BLOCK_SIZE, BLOCK_SIZE), #Top-right
    pygame.Rect(0, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), #Bottom-left
    pygame.Rect(SCREEN_WIDTH - BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE) #Bottom-right
    ]

#Initialize Scores
last_player_hit = None
score_left = 0 #Player 1
score_right = 0 #Player 2
score_bottom = 0 #Player 3
score_top = 0 #Player 4

def assign_point(last_player_hit):
    global score_left, score_right, score_bottom, score_top
    if last_player_hit == 0:
        score_left += 1  #Player 1 scores
    elif last_player_hit == 1:
        score_right += 1  #Player 2 scores
    elif last_player_hit == 2:
        score_bottom += 1  #Player 3 scores
    elif last_player_hit == 3:
        score_top += 1  #Player 4 scores
    score_sound.play() 
  
def increase_ball_speed(ball_dx, ball_dy):
    angle_adjustment = random.uniform(-0.1, 0.1)
    new_dx = ball_dx * BALL_SPEED_INCREMENT + angle_adjustment
    new_dy = ball_dy * BALL_SPEED_INCREMENT + angle_adjustment

    total_speed = math.sqrt(new_dx**2 + new_dy**2)
    if total_speed > BALL_MAX_SPEED:
        factor = BALL_MAX_SPEED / total_speed
        new_dx *= factor
        new_dy *= factor
    return new_dx, new_dy

#Resets the ball at the start of each round
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy, last_player_hit
    ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    
    angle = random.uniform(0, 2 * math.pi)
    
    ball_dx = BALL_BASE_SPEED * math.cos(angle)
    ball_dy = BALL_BASE_SPEED * math.sin(angle)
    
    last_player_hit = None
    
def display_countdown(seconds):
    font = pygame.font.Font(None, 120)
    start_time = pygame.time.get_ticks()
    elapsed_time = 0

    # Create a semi-transparent overlay with game-like colors
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((90, 90, 90, 150))

    while elapsed_time < seconds * 1000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = seconds - elapsed_time // 1000

        # Draw the current game state behind the countdown
        screen.fill(BLACK)  # Background
        for i, paddle in enumerate(paddles):
            colors = [RED, BLUE, GREEN, ORANGE]
            pygame.draw.rect(screen, colors[i], paddle)
        for block in blocks:
            pygame.draw.rect(screen, WHITE, block)
        pygame.draw.rect(screen, WHITE, ball)

        # Draw the semi-transparent overlay
        screen.blit(overlay, (0, 0))

        countdown_text = font.render(str(remaining_time), True, YELLOW)
        text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(countdown_text, text_rect)

        pygame.display.flip()
        clock.tick(60)

        
#Sets ball collision interactions with paddles/blocks
def block_collisions(block):
    global ball_x, ball_y, ball_dx, ball_dy
    if ball.colliderect(block):
        hit_sound.play()
        ball_dx, ball_dy = increase_ball_speed(ball_dx, ball_dy)
        #Left Side Collision
        if ball_dx > 0 and ball.right <= block.left + ball_dx:
            ball_x = block.left - BALL_SIZE
            ball_dx *= -1
        #Right Side Collision
        elif ball_dx < 0 and ball.left >= block.right + ball_dx:
            ball_x = block.right
            ball_dx *= -1
        #Top Collision
        if ball_dy > 0 and ball.bottom <= block.top + ball_dy:
            ball_y = block.top - BALL_SIZE
            ball_dy *= -1
        #Bottom Collision
        if ball_dy < 0 and ball.top >= block.bottom + ball_dy:
            ball_y = block.bottom
            ball_dy *= -1

#Game state
current_state = MENU
countdown_done = False  #flag to manage the countdown

#Game duration (in seconds)
GAME_DURATION = 120  # Set to 60 for 1 minute of play
game_start_time = None

game_timer_paused = False  #Initialize paused flag
paused_time = 0  #Time elapsed when the game was paused

while True:

    #Quit the game immediately if the current state is "quit"
    if current_state == "quit":
        pygame.quit()
        sys.exit()

    #Main Menu State
    elif current_state == MENU:
        draw_menu(screen)
        current_state = handle_menu_input()

        #Reset game state for a fresh start
        countdown_done = False
        game_start_time = None
        paused_time = 0
        game_timer_paused = False
        
        ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        ball_dx, ball_dy = BALL_BASE_SPEED, BALL_BASE_SPEED
        ball.x, ball.y = ball_x, ball_y
        
        paddles[0].y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2  #Left paddle
        paddles[1].y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2  #Right paddle
        paddles[2].x = SCREEN_WIDTH // 2 - PADDLE_HEIGHT // 2   #Bottom paddle
        paddles[3].x = SCREEN_WIDTH // 2 - PADDLE_HEIGHT // 2   #Top paddle
        
        score_left = score_right = score_bottom = score_top = 0

    #Playing State
    elif current_state == PLAYING:
        if not countdown_done:
            display_countdown(3)
            reset_ball()
            countdown_done = True
            game_start_time = pygame.time.get_ticks()  #Initialize timer AFTER countdown

        #Resume timer after pause
        if game_timer_paused:
            game_start_time = pygame.time.get_ticks() - paused_time
            game_timer_paused = False

        #Timer logic
        if countdown_done and game_start_time is not None:
            elapsed_time = (pygame.time.get_ticks() - game_start_time) // 1000
            remaining_time = GAME_DURATION - elapsed_time

            if remaining_time <= 0:
                current_state = GAME_OVER

        #Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_state = "quit"
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_state = PAUSED

        #Update game state
        ball_x += ball_dx
        ball_y += ball_dy
        ball.x = ball_x
        ball.y = ball_y

        #Ball collision with paddles
        for paddle in paddles:
            block_collisions(paddle)

        #Ball collision with blocks
        for block in blocks:
            block_collisions(block)

        #Move paddles
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddles[0].top > BLOCK_SIZE:
            paddles[0].y -= PADDLE_SPEED
        if keys[pygame.K_s] and paddles[0].bottom < SCREEN_HEIGHT - BLOCK_SIZE:
            paddles[0].y += PADDLE_SPEED
        if keys[pygame.K_UP] and paddles[1].top > BLOCK_SIZE:
            paddles[1].y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and paddles[1].bottom < SCREEN_HEIGHT - BLOCK_SIZE:
            paddles[1].y += PADDLE_SPEED
        if keys[pygame.K_c] and paddles[2].left > BLOCK_SIZE:
            paddles[2].x -= PADDLE_SPEED
        if keys[pygame.K_b] and paddles[2].right < SCREEN_WIDTH - BLOCK_SIZE:
            paddles[2].x += PADDLE_SPEED
        if keys[pygame.K_u] and paddles[3].left > BLOCK_SIZE:
            paddles[3].x -= PADDLE_SPEED
        if keys[pygame.K_o] and paddles[3].right < SCREEN_WIDTH - BLOCK_SIZE:
            paddles[3].x += PADDLE_SPEED

        #Update last player hit
        if ball.colliderect(paddles[0]):
            last_player_hit = 0
        if ball.colliderect(paddles[1]):
            last_player_hit = 1
        if ball.colliderect(paddles[2]):
            last_player_hit = 2
        if ball.colliderect(paddles[3]):
            last_player_hit = 3

        #Ball out of bounds
        if ball_x < 0 or ball_x > SCREEN_WIDTH or ball_y < 0 or ball_y > SCREEN_HEIGHT:
            assign_point(last_player_hit)
            reset_ball()
            display_countdown(3)

        #Draw Background
        screen.fill(BLACK)

        #Draw Ball
        pygame.draw.rect(screen, WHITE, ball)

        #Draw Paddles
        pygame.draw.rect(screen, RED, paddles[0])
        pygame.draw.rect(screen, BLUE, paddles[1])
        pygame.draw.rect(screen, GREEN, paddles[2])
        pygame.draw.rect(screen, ORANGE, paddles[3])

        #Draw Corner Blocks
        for block in blocks:
            pygame.draw.rect(screen, WHITE, block)

        #Draw Player Scores
        font = pygame.font.Font(None, 74)
        text_left = font.render("P1: " + str(score_left), True, GRAY)
        text_right = font.render("P2: " + str(score_right), True, GRAY)
        text_bottom = font.render("P3: " + str(score_bottom), True, GRAY)
        text_top = font.render("P4: " + str(score_top), True, GRAY)
        screen.blit(text_left, (50, SCREEN_HEIGHT // 2 - 25))
        screen.blit(text_right, (SCREEN_WIDTH - 170, SCREEN_HEIGHT // 2 - 25))
        screen.blit(text_bottom, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 95))
        screen.blit(text_top, (SCREEN_WIDTH // 2 - 60, 50))

        #Display timer
        font = pygame.font.Font(None, 36)
        time_text = font.render(f"Time Left: {remaining_time}s", True, WHITE)
        screen.blit(time_text, (10, 10))

        #Update display
        pygame.display.flip()
        clock.tick(60)

    #Paused State
    elif current_state == PAUSED:
        paused_time = pygame.time.get_ticks() - game_start_time
        game_timer_paused = True

        draw_pause_menu(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                current_state = "quit"
                break
            new_state = handle_pause_input(event)
            if new_state == "quit":
                current_state = "quit"
                break
            elif new_state == PLAYING:
                display_countdown(3)
                current_state = PLAYING
            elif new_state == MENU:
                current_state = MENU

    #Game Over State
    elif current_state == GAME_OVER:
        total_scores = [score_left, score_right, score_bottom, score_top]
        new_state = draw_game_over_screen(screen, total_scores)

        if new_state == "menu":
            current_state = MENU
        elif new_state == "quit":
            current_state = "quit"

        #Reset game state
        ball_x, ball_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        ball_dx, ball_dy = BALL_BASE_SPEED, BALL_BASE_SPEED
        score_left = score_right = score_bottom = score_top = 0
        game_start_time = None

    #Fallback for unexpected states
    else:
        print(f"Unexpected state: {current_state}.")
        pygame.quit()
        sys.exit()

