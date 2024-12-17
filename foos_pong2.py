import pygame
import sys
import math
import random
from pause_menu import PauseMenu
from game_states import GameState

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BALL_SPEED = 5
PADDLE_SPEED = 5
BALL_RADIUS = 10
BLOCK_SIZE = 40  # Size for the square blocks in the corners
PADDLE_WIDTH = 100  # Vertical paddle width
PADDLE_HEIGHT = 100  # Horizontal paddle height
VERTICAL_PADDLE_WIDTH = BLOCK_SIZE
VERTICAL_PADDLE_HEIGHT = 100  # Maintain height for vertical paddles
BALL_SPEED_INCREMENT = 1.25  # 5% speed increase per hit
MAX_BALL_SPEED = 100  # Optional: Cap the ball speed
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)
SHRINK_PADDLE_HEIGHT = PADDLE_HEIGHT/2 #% of size change when power up activated

pygame.init()

# Sound effects
hit_sound = pygame.mixer.Sound("audio/hit_paddle.wav")
score_sound = pygame.mixer.Sound("audio/sound_goal.wav")


class PongGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pause_menu = PauseMenu(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.set_caption("Pong")

        self.clock = pygame.time.Clock()

        # Ball position and velocity
        self.reset_ball()

        # Track the last player to hit the ball
        self.last_player_hit = None  

        # Vertical paddles (left and right sides)
        self.paddle_left_y = SCREEN_HEIGHT // 2  # Left paddle (Player 1)
        self.paddle_right_y = SCREEN_HEIGHT // 2  # Right paddle (Player 2)

        # Horizontal paddles (top and bottom sides)
        self.paddle_top_x = SCREEN_WIDTH // 2  # Top paddle (Player 4)
        self.paddle_bottom_x = SCREEN_WIDTH // 2  # Bottom paddle (Player 3)

        # Scores
        self.score_left = 0  # Player 1
        self.score_right = 0  # Player 2
        self.score_bottom = 0  # Player 3
        self.score_top = 0  # Player 4

        self.shrink_p1 = False
        self.shrink_p2 = False
        self.shrink_p3 = False
        self.shrink_p4 = False

        # Square block positions (top-left, top-right, bottom-left, bottom-right)
        self.blocks = [
            (0, 0),  # Top-left
            (SCREEN_WIDTH - BLOCK_SIZE, 0),  # Top-right
            (0, SCREEN_HEIGHT - BLOCK_SIZE),  # Bottom-left
            (SCREEN_WIDTH - BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE)  # Bottom-right
        ]

    def draw(self):
        self.screen.fill(BLACK)

        p1_paddle_height = PADDLE_HEIGHT // 2 if self.shrink_p1 else PADDLE_WIDTH
        p2_paddle_height = PADDLE_HEIGHT // 2 if self.shrink_p2 else PADDLE_WIDTH
        p3_paddle_height = PADDLE_HEIGHT // 2 if self.shrink_p3 else VERTICAL_PADDLE_HEIGHT
        p4_paddle_height = PADDLE_HEIGHT // 2 if self.shrink_p4 else VERTICAL_PADDLE_HEIGHT

        # Draw ball
        pygame.draw.circle(self.screen, WHITE, (self.ball_x, self.ball_y), BALL_RADIUS)

        # Draw vertical paddles (Player 1 and Player 2) flush with the edges
        pygame.draw.rect(self.screen, RED, (0, self.paddle_left_y - p1_paddle_height // 2, BLOCK_SIZE, p1_paddle_height))  # Left paddle (Player 1)
        pygame.draw.rect(self.screen, BLUE, (SCREEN_WIDTH - BLOCK_SIZE, self.paddle_right_y - p2_paddle_height // 2, BLOCK_SIZE, p2_paddle_height))  # Right paddle (Player 2)

        # Draw horizontal paddles (Player 4 and Player 3) flush with the edges
        pygame.draw.rect(self.screen, GREEN, (self.paddle_bottom_x - p3_paddle_height // 2, SCREEN_HEIGHT - BLOCK_SIZE, p3_paddle_height, BLOCK_SIZE))  # Bottom paddle (Player 3)
        pygame.draw.rect(self.screen, ORANGE, (self.paddle_top_x - p4_paddle_height // 2, 0, p4_paddle_height, BLOCK_SIZE))  # Top paddle (Player 4)
        

        # Draw square blocks in the corners
        for block in self.blocks:
            pygame.draw.rect(self.screen, GRAY, (*block, BLOCK_SIZE, BLOCK_SIZE))

        # Draw scores with player numbers
        font = pygame.font.Font(None, 74)
        text_left = font.render("P1: " + str(self.score_left), True, WHITE)
        text_right = font.render("P2: " + str(self.score_right), True, WHITE)
        text_bottom = font.render("P3: " + str(self.score_bottom), True, WHITE)
        text_top = font.render("P4: " + str(self.score_top), True, WHITE)

        # Display the scores in different corners
        self.screen.blit(text_left, (50, SCREEN_HEIGHT // 2 - 50))  # Player 1 score (left)
        self.screen.blit(text_right, (SCREEN_WIDTH - 180, SCREEN_HEIGHT // 2 - 50))  # Player 2 score (right)
        self.screen.blit(text_bottom, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100))  # Player 3 score (bottom)
        self.screen.blit(text_top, (SCREEN_WIDTH // 2 - 50, 50))  # Player 4 score (top)

        pygame.display.flip()




    def update(self):
        # Ball movement
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Adjust paddle heights based on whether they are shrunk
        p1_paddle_height = PADDLE_HEIGHT // 2 if self.shrink_p1 else VERTICAL_PADDLE_HEIGHT
        p2_paddle_height = PADDLE_HEIGHT // 2 if self.shrink_p2 else VERTICAL_PADDLE_HEIGHT
        p3_paddle_width = PADDLE_WIDTH // 2 if self.shrink_p3 else PADDLE_WIDTH
        p4_paddle_width = PADDLE_WIDTH // 2 if self.shrink_p4 else PADDLE_WIDTH

        # Ball collision with Player 1's paddle (Left)
        if self.ball_dx < 0 and self.ball_x - BALL_RADIUS <= BLOCK_SIZE:
            if self.paddle_left_y - p1_paddle_height // 2 <= self.ball_y <= self.paddle_left_y + p1_paddle_height // 2:
                self.ball_dx *= -1
                self.randomize_angle()
                self.increase_ball_speed()
                hit_sound.play()
                self.last_player_hit = 1

        # Ball collision with Player 2's paddle (Right)
        elif self.ball_dx > 0 and self.ball_x + BALL_RADIUS >= SCREEN_WIDTH - BLOCK_SIZE:
            if self.paddle_right_y - p2_paddle_height // 2 <= self.ball_y <= self.paddle_right_y + p2_paddle_height // 2:
                self.ball_dx *= -1
                self.randomize_angle()
                self.increase_ball_speed()
                hit_sound.play()
                self.last_player_hit = 2

        # Ball collision with Player 4's paddle (Top)
        if self.ball_dy < 0 and self.ball_y - BALL_RADIUS <= BLOCK_SIZE:
            if self.paddle_top_x - p4_paddle_width // 2 <= self.ball_x <= self.paddle_top_x + p4_paddle_width // 2:
                self.ball_dy *= -1
                self.randomize_angle()
                self.increase_ball_speed()
                hit_sound.play()
                self.last_player_hit = 4

        # Ball collision with Player 3's paddle (Bottom)
        elif self.ball_dy > 0 and self.ball_y + BALL_RADIUS >= SCREEN_HEIGHT - BLOCK_SIZE:
            if self.paddle_bottom_x - p3_paddle_width // 2 <= self.ball_x <= self.paddle_bottom_x + p3_paddle_width // 2:
                self.ball_dy *= -1
                self.randomize_angle()
                self.increase_ball_speed()
                hit_sound.play()
                self.last_player_hit = 3

        # Check if the ball has gone out of the screen
        if self.ball_x < 0 or self.ball_x > SCREEN_WIDTH or self.ball_y < 0 or self.ball_y > SCREEN_HEIGHT:
            self.assign_point()
            self.reset_ball()

        # Ball collision with square blocks in the corners
        self.check_block_collisions()

    def check_block_collisions(self):
        for block_x, block_y in self.blocks:
            if block_x <= self.ball_x <= block_x + BLOCK_SIZE and block_y <= self.ball_y <= block_y + BLOCK_SIZE:
                # Reflect both the x and y velocities when the ball hits a square corner
                self.ball_dx *= -1
                self.ball_dy *= -1
                self.randomize_angle()  # Add slight random angle adjustment after corner collision
                hit_sound.play()

    def increase_ball_speed(self):
        """Increase the ball's speed slightly after each hit."""
        new_dx = self.ball_dx * BALL_SPEED_INCREMENT
        new_dy = self.ball_dy * BALL_SPEED_INCREMENT

        # Normalize speed to prevent diagonal bias
        speed = math.sqrt(new_dx**2 + new_dy**2)
        if speed > MAX_BALL_SPEED:  # Optional speed cap
            speed = MAX_BALL_SPEED

        self.ball_dx = (new_dx / speed) * speed
        self.ball_dy = (new_dy / speed) * speed

    def assign_point(self):
        """Award a point to the last player who hit the ball."""
        if self.last_player_hit == 1:
            self.score_left += 1  # Player 1 scores
        elif self.last_player_hit == 2:
            self.score_right += 1  # Player 2 scores
        elif self.last_player_hit == 3:
            self.score_bottom += 1  # Player 3 scores
        elif self.last_player_hit == 4:
            self.score_top += 1  # Player 4 scores
        score_sound.play()  # Play score sound effect

    def randomize_angle(self):
        """ Introduce a slight random angle to avoid perfect vertical or horizontal motion. """
        angle_adjustment = random.uniform(-0.1, 0.1)  # Small angle adjustment
        new_dx = self.ball_dx + angle_adjustment
        new_dy = self.ball_dy + angle_adjustment

        # Normalize the speed to maintain constant velocity
        speed = math.sqrt(new_dx**2 + new_dy**2)
        self.ball_dx = (new_dx / speed) * BALL_SPEED
        self.ball_dy = (new_dy / speed) * BALL_SPEED

    def handle_input(self, keys):
        # Player 1 (left paddle) movement limits based on top and bottom blocks
        if keys[pygame.K_w] and self.paddle_left_y - VERTICAL_PADDLE_HEIGHT // 2 > BLOCK_SIZE:  # Player 1 (up)
            self.paddle_left_y -= PADDLE_SPEED
        if keys[pygame.K_s] and self.paddle_left_y + VERTICAL_PADDLE_HEIGHT // 2 < SCREEN_HEIGHT - BLOCK_SIZE:  # Player 1 (down)
            self.paddle_left_y += PADDLE_SPEED

        # Player 2 (right paddle) movement limits based on top and bottom blocks
        if keys[pygame.K_UP] and self.paddle_right_y - VERTICAL_PADDLE_HEIGHT // 2 > BLOCK_SIZE:  # Player 2 (up)
            self.paddle_right_y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and self.paddle_right_y + VERTICAL_PADDLE_HEIGHT // 2 < SCREEN_HEIGHT - BLOCK_SIZE:  # Player 2 (down)
            self.paddle_right_y += PADDLE_SPEED

        # Player 4 (top paddle) movement limits based on left and right blocks
        if keys[pygame.K_a] and self.paddle_top_x - PADDLE_WIDTH // 2 > BLOCK_SIZE:  # Player 4 (left)
            self.paddle_top_x -= PADDLE_SPEED
        if keys[pygame.K_d] and self.paddle_top_x + PADDLE_WIDTH // 2 < SCREEN_WIDTH - BLOCK_SIZE:  # Player 4 (right)
            self.paddle_top_x += PADDLE_SPEED

        # Player 3 (bottom paddle) movement limits based on left and right blocks
        if keys[pygame.K_j] and self.paddle_bottom_x - PADDLE_WIDTH // 2 > BLOCK_SIZE:  # Player 3 (left)
            self.paddle_bottom_x -= PADDLE_SPEED
        if keys[pygame.K_l] and self.paddle_bottom_x + PADDLE_WIDTH // 2 < SCREEN_WIDTH - BLOCK_SIZE:  # Player 3 (right)
            self.paddle_bottom_x += PADDLE_SPEED
        
        # Paddle shrink power-up activation
        if keys[pygame.K_TAB]:  # Player 1 activates shrink
            self.shrink_p2 = True
            self.shrink_p3 = True
            self.shrink_p4 = True

        if keys[pygame.K_RSHIFT]:  # Player 2 activates shrink
            self.shrink_p1 = True
            self.shrink_p3 = True
            self.shrink_p4 = True

        if keys[pygame.K_u]:  # Player 3 activates shrink
            self.shrink_p1 = True
            self.shrink_p2 = True
            self.shrink_p4 = True

        if keys[pygame.K_LSHIFT]:  # Player 4 activates shrink
            self.shrink_p1 = True
            self.shrink_p2 = True
            self.shrink_p3 = True

    def reset_ball(self):
        self.ball_x = SCREEN_WIDTH // 2
        self.ball_y = SCREEN_HEIGHT // 2
        self.last_player_hit = None  # Reset the last player hit

        self.shrink_p1 = False
        self.shrink_p2 = False
        self.shrink_p3 = False
        self.shrink_p4 = False

        # Randomize the ball's initial direction (angle)
        angle = random.uniform(math.radians(30), math.radians(60))
        direction = random.choice([-1, 1])
        self.ball_dx = BALL_SPEED * math.cos(angle) * direction
        self.ball_dy = BALL_SPEED * math.sin(angle) * random.choice([-1, 1])

    def run(self):
        resume_delay_timer = 0
        last_drawn_second = -1
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    # Toggle pause state
                    self.pause_menu.paused = not self.pause_menu.paused
                    resume_delay_timer = 0
                    last_drawn_second = -1
                
                # Handle pause menu input when paused
                if self.pause_menu.paused:
                    menu_state = self.pause_menu.handle_pause_input(event)
                    if menu_state == GameState.MENU:
                        # Exit the game loop and signal the main menu
                        return GameState.MENU

            if not self.pause_menu.paused:
                current_second = max(0, 3 - (resume_delay_timer // 60))

                if resume_delay_timer < 180:
                    if current_second != last_drawn_second:
                        self.draw()  # Draw game state

                        # Use pause menu's countdown drawing method
                        self.pause_menu.draw_countdown(self.screen, current_second)

                        last_drawn_second = current_second

                    resume_delay_timer += 1
                else:
                    keys = pygame.key.get_pressed()
                    self.handle_input(keys)
                    self.update()
                    self.draw()
            else:
                # Draw pause menu when paused
                self.pause_menu.draw_pause_menu()

            self.clock.tick(60)

if __name__ == "__main__":
    PongGame().run()