import pygame
from game_states import MENU, PLAYING, GAME_OVER

# Pause menu state
pause_menu_state = {
    "selected_item": 0,
    "menu_items": ["Resume", "Main Menu", "Quit"],
    "screen_width": 600,  
    "screen_height": 600, 
}

# Colors and Fonts
RED, BLUE, ORANGE, GREEN, YELLOW, BLACK, WHITE = (
    (255, 0, 0), (0, 0, 255), (255, 165, 0), (0, 255, 0),
    (255, 255, 0), (0, 0, 0), (255, 255, 255)
)

def draw_pause_alternate_colors(screen, text, y_position, font):
    colors = [RED, BLUE, ORANGE, GREEN]
    total_width = sum(font.render(letter, True, colors[i % len(colors)]).get_width() for i, letter in enumerate(text))
    x_position = (pause_menu_state["screen_width"] // 2) - (total_width // 2)

    for i, letter in enumerate(text):
        rendered_letter = font.render(letter, True, colors[i % len(colors)])
        screen.blit(rendered_letter, (x_position, y_position))
        x_position += rendered_letter.get_width()

def draw_pause_menu(screen):
    screen.fill(BLACK)
    title_font = pygame.font.Font("Fonts/upheavtt.ttf", 50) 
    small_font = pygame.font.Font("Fonts/upheavtt.ttf", 30)

    draw_pause_alternate_colors(screen, "Paused", 100, title_font)

    for index, item in enumerate(pause_menu_state["menu_items"]):
        color = YELLOW if index == pause_menu_state["selected_item"] else WHITE
        label = small_font.render(item, True, color)
        screen.blit(label, (pause_menu_state["screen_width"] // 2 - label.get_width() // 2, 200 + index * 50)) 

    pygame.display.flip()

def handle_pause_input(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            pause_menu_state["selected_item"] = (pause_menu_state["selected_item"] - 1) % len(pause_menu_state["menu_items"])
        elif event.key == pygame.K_DOWN:
            pause_menu_state["selected_item"] = (pause_menu_state["selected_item"] + 1) % len(pause_menu_state["menu_items"])
        elif event.key == pygame.K_RETURN:
            selected_item = pause_menu_state["menu_items"][pause_menu_state["selected_item"]]
            if selected_item == "Resume":
                return PLAYING
            elif selected_item == "Main Menu":
                return MENU
            elif selected_item == "Quit":
                # print("Pause Menu Quit Selected")  # Debugging
                return "quit"
    return None



