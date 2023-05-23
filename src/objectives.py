import pygame

from src.blocks import GameObject


class Objective(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "objective"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = [230, 230, 250, 255]

        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))
        self.passed = False

    def if_passed(self):
        return pygame.sprite.spritecollideany(self, self.game_map.player)

    def update(self):
        if self.if_passed():
            self.color = [50, 205, 50, 255]
            self.image = pygame.Surface((self.width_scaled, self.height_scaled))
            self.image.fill(self.color)
            self.passed = True

