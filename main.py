import pygame
import sys
from main_menu import Menu
from foos_pong2 import PongGame
from game_states import GameState
from database.leaderboard import setup_database

class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.menu = Menu(self.screen)
        self.pong_game = None
        self.current_state = GameState.MENU

    def run(self):
        while True:
            if self.current_state == GameState.MENU:
                self.current_state = self.menu.handle_input()
                self.menu.draw()

            elif self.current_state == GameState.PLAYING:
                if self.pong_game is None:
                    self.pong_game = PongGame()

                next_state = self.pong_game.run()

                if next_state == GameState.MENU:
                    self.current_state = GameState.MENU
                    self.pong_game = None

            elif self.current_state == GameState.GAME_OVER:
                pygame.quit()
                sys.exit()

            self.clock.tick(60)

if __name__ == "__main__":
    setup_database()
    game = Game()
    game.run()