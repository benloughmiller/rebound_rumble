import pygame
from database.leaderboard import get_leaderboard
from game_states import MENU, PLAYING, GAME_OVER

menu_state = {
    "selected_item": 0,
    "menu_items": ["Play", "Quit"],
    "screen_width": 600,
    "screen_height": 600,
}

RED, BLUE, ORANGE, GREEN, YELLOW, BLACK, GRAY, WHITE = (
    (255, 0, 0), (0, 0, 255), (255, 165, 0), (0, 255, 0),
    (255, 255, 0), (0, 0, 0), (125, 125, 125), (255, 255, 255)
)

def draw_title_alternate_colors(screen, text, y_position, title_font):
    colors = [RED, BLUE, ORANGE, GREEN]
    total_width = sum(title_font.render(letter, True, colors[i % len(colors)]).get_width() for i, letter in enumerate(text))
    x_position = (menu_state["screen_width"] // 2) - (total_width // 2)

    for i, letter in enumerate(text):
        rendered_letter = title_font.render(letter, True, colors[i % len(colors)])
        screen.blit(rendered_letter, (x_position, y_position))
        x_position += rendered_letter.get_width()

#Draws the leaderboard for the program
def draw_leaderboard(screen):
    small_font = pygame.font.Font("Fonts/upheavtt.ttf", 30)
    leaders = get_leaderboard()
    leaderboard_title = small_font.render("Leaderboard", True, GRAY)
    screen.blit(leaderboard_title, (menu_state["screen_width"] // 2 - leaderboard_title.get_width() // 2, 300))

    for index, (player_name, score) in enumerate(leaders[:5]):
        leaderboard_text = small_font.render(f"{index + 1}. {player_name}: {score}", True, WHITE)
        screen.blit(leaderboard_text, (menu_state["screen_width"] // 2 - leaderboard_text.get_width() // 2, 340 + index * 30))

def draw_menu(screen):
    screen.fill(BLACK)


    title_font = pygame.font.Font("Fonts/upheavtt.ttf", 50)
    small_font = pygame.font.Font("Fonts/upheavtt.ttf", 30) 


    draw_title_alternate_colors(screen, "Rebound Rumble", 50, title_font) 


    for index, item in enumerate(menu_state["menu_items"]):
        color = YELLOW if index == menu_state["selected_item"] else WHITE
        label = small_font.render(item, True, color)
        screen.blit(label, (menu_state["screen_width"] // 2 - label.get_width() // 2, 150 + index * 50))  # Adjusted positions

    draw_leaderboard(screen)

    pygame.display.flip()

def handle_menu_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                menu_state["selected_item"] = (menu_state["selected_item"] + 1) % len(menu_state["menu_items"])
            if event.key == pygame.K_UP:
                menu_state["selected_item"] = (menu_state["selected_item"] - 1) % len(menu_state["menu_items"])
            if event.key == pygame.K_RETURN:
                if menu_state["menu_items"][menu_state["selected_item"]] == "Play":
                    return PLAYING
                elif menu_state["menu_items"][menu_state["selected_item"]] == "Quit":
                    return "quit"
    return MENU

