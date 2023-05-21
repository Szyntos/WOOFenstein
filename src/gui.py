import pygame


class Gui:
    def __init__(self, game_map, width, height):
        filename = "./img/gui.png"
        gui = pygame.image.load(filename).convert_alpha()
        self.gui = pygame.transform.scale(gui, (width, height))
        self.game_map = game_map

    def get_game_statistics(self):
        player_hp = self.game_map.player.sprite.health
        enemy_count = len(self.game_map.enemies.sprites())

    def draw_gui(self):
        self.game_map.screen.blit(self.gui, (0, 0))
