import pygame
import time
import json


class Gui:
    def __init__(self, game_map, window_width, window_height,
                 scale, map_width, map_height):
        filename = "./img/gui.png"
        gui = pygame.image.load(filename).convert_alpha()
        self.gui = pygame.transform.scale(gui, (window_width, window_height))
        filename = "./img/game_over.jpg"
        game_over = pygame.image.load(filename).convert_alpha()
        self.game_over = pygame.transform.scale(game_over, (window_width, window_height))
        filename = "./img/won.jpg"
        won = pygame.image.load(filename).convert_alpha()
        self.won = pygame.transform.scale(won, (window_width, window_height))
        self.game_map = game_map
        self.time_initialized = time.time()
        self.scale = scale
        self.map_width = map_width
        self.map_height = map_height
        self.font = pygame.font.Font('digital-7/digital-7 (mono).ttf', int(40*self.scale))

    def get_game_statistics(self):
        player_hp = self.game_map.player.sprite.health
        enemy_count = len(self.game_map.enemies.sprites())
        time_passed = time.time() - self.time_initialized
        return player_hp, enemy_count, time_passed

    def draw_gui(self):
        self.game_map.screen.blit(self.gui, (0, 0))
        h = 0.85 * self.map_height * self.scale
        dh = 0.07 * self.map_height * self.scale
        w = 0.4 * self.map_width * self.scale
        dw = 0.8 * self.map_width * self.scale
        player_hp, enemy_count, time_passed = self.get_game_statistics()
        player_hp = self.font.render("Player Health: " + str(player_hp), True, "Red")
        self.game_map.screen.blit(player_hp, (w, h))
        enemy_count = self.font.render("Enemies Left: " + str(enemy_count), True, "Red")
        self.game_map.screen.blit(enemy_count, (w, h + dh))
        time_passed = self.font.render("Time Passed: " + str(int(time_passed)), True, "Red")
        self.game_map.screen.blit(time_passed, (w + dw, h))

    def draw_game_over(self):
        self.game_map.screen.blit(self.game_over, (0, 0))

    def draw_won(self):
        self.game_map.screen.blit(self.won, (0, 0))
