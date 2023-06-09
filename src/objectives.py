import pygame

from src.blocks import GameObject
from src.utils import hex_to_rgb

import colorsys


class Objective(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "objective"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        # self.color = hex_to_rgb("#EBC7E6") + [255]
        (r, g, b) = colorsys.hsv_to_rgb(0, 1.0, 1.0)
        self.color = [int(255 * r), int(255 * g), int(255 * b)] + [255]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))
        self.passed = False
        self.t = 0

    def if_passed(self):
        return pygame.sprite.spritecollideany(self, self.game_map.player) or self.passed

    def update(self):

        if self.if_passed():
            self.color = [50, 100, 50, 255]
            self.passed = True
        else:
            self.t += 0.02
            (r, g, b) = colorsys.hsv_to_rgb(self.t, 1.0, 1.0)
            self.color = [int(255 * r), int(255 * g), int(255 * b)] + [255]
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.image.fill(self.color)
