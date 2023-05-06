import pygame

from src.utils import hex_to_rgb

constructors = {}


def register_block(constructor):
    constructors[constructor.__name__] = constructor
    return constructor


def get_block_constructors():
    return {key: value for key, value in constructors.items()}


class GameObject(pygame.sprite.Sprite):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__()
        self.screen = screen
        self.game_map = game_map
        self.width = width
        self.height = height
        self.width_scaled = width * self.game_map.scale
        self.height_scaled = height * self.game_map.scale
        self.x = x
        self.y = y
        self.x_scaled = x * self.game_map.scale + self.game_map.vector[0]
        self.y_scaled = y * self.game_map.scale + self.game_map.vector[1]
        self.orientation = 0
        self.type = None
        self.color = (0, 0, 0, 0)


@register_block
class Box(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "opaque"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = hex_to_rgb("#3F3734") + [122]
        # self.color = [168, 168, 168, 255]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass


@register_block
class RedBox(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "opaque"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = [120, 70, 70, 255]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass


@register_block
class Glass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "semitransparent"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = hex_to_rgb("#1c319f") + [122]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass


@register_block
class RedGlass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "semitransparent"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = hex_to_rgb("#aa319f") + [50]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass


@register_block
class GreenGlass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "semitransparent"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = hex_to_rgb("#1caa9f") + [50]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass
