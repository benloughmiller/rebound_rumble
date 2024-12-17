import sys
import pygame
import sqlite3

# Screen size and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

#Save player scores to the database
def save_score(player_name, score):
    connection = sqlite3.connect("database/leaderboard.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO leaderboard (player_name, score) VALUES (?, ?)", (player_name, score))
    connection.commit()
    connection.close()

#Draws the screen when the game ends
def draw_game_over_screen(screen, scores):
    """Draw the game over screen where players can enter their names."""
    title_font = pygame.font.Font("Fonts/upheavtt.ttf", 50) 
    small_font = pygame.font.Font("Fonts/upheavtt.ttf", 30)

    player_names = [""] * 4
    input_active = [True] * 4
    current_player = 0

    while any(input_active):
        screen.fill(BLACK)

        game_over_text = title_font.render("Game Over", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 50))

        prompt_text = small_font.render(f"Player {current_player + 1}, Enter Your Name:", True, WHITE)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 150))

        for i, name in enumerate(player_names):
            color = YELLOW if i == current_player else WHITE
            name_text = small_font.render(f"Player {i + 1}: {name} ({scores[i]})", True, color)
            screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 200 + i * 50))

        pygame.display.flip()

        #Event Handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if input_active[current_player]:
                    if event.key == pygame.K_RETURN:
                        input_active[current_player] = False
                        current_player = (current_player + 1) % 4
                    elif event.key == pygame.K_BACKSPACE:
                        player_names[current_player] = player_names[current_player][:-1]
                    else:
                        player_names[current_player] += event.unicode

    save_scores_to_database(player_names, scores)

    return "menu"

def save_scores_to_database(player_names, scores):
    """Save the players' names and scores to the database."""
    connection = sqlite3.connect("database/leaderboard.db")
    cursor = connection.cursor()

    for name, score in zip(player_names, scores):
        cursor.execute("""
            INSERT INTO leaderboard (player_name, score)
            VALUES (?, ?)
            ON CONFLICT(player_name) DO UPDATE SET score = excluded.score
        """, (name, score))

    connection.commit()
    connection.close()

    return "menu"
