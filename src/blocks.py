import time

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
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))
        self.orientation = 0
        self.type = None
        self.color = (0, 0, 0, 0)


@register_block
class Border(GameObject):
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
class Door(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "opaque"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = hex_to_rgb("#B67107") + [122]
        # self.color = [168, 168, 168, 255]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))
        self.time_to_open = 20
        self.open_orientation = "horizontal" if self.width > self.height else "vertical"
        self.width_org = self.width
        self.height_org = self.width
        self.tmp = time.time()
        self.closed = 1
        self.open_size = 20 * self.game_map.scale
        self.open_leeway = 400 * self.game_map.scale
        self.open_hit_box = (GameObject(screen, game_map, width, height + self.open_leeway, x, y-self.open_leeway/2)
                             if self.width > self.height else
                             GameObject(screen, game_map, width + self.open_leeway, height, x-self.open_leeway/2, y))

    def update_shape(self):
        self.width_scaled = self.width * self.game_map.scale
        self.height_scaled = self.height * self.game_map.scale
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def open(self):
        if self.open_orientation == "horizontal" and self.closed:
            if self.width > self.open_size:
                self.width = max(self.width - (self.width_org - self.open_size) / self.time_to_open, self.open_size)
            else:
                self.closed = 0
        elif self.open_orientation == "vertical" and self.closed:
            if self.height > self.open_size:
                self.height = max(self.height - (self.height_org - self.open_size) / self.time_to_open, self.open_size)
            else:
                self.closed = 0
        self.update_shape()

    def close(self):
        if self.open_orientation == "horizontal" and not self.closed:
            if self.width < self.width_org:
                self.width = min(self.width + (self.width_org - self.open_size) / self.time_to_open, self.width_org)
            else:
                self.closed = 1
        elif self.open_orientation == "vertical" and not self.closed:
            if self.height < self.height_org:
                self.height = min(self.height + (self.height_org - self.open_size) / self.time_to_open, self.height_org)
            else:
                self.closed = 1
        self.update_shape()

    def is_player_close(self):
        return pygame.sprite.spritecollide(self.open_hit_box, self.game_map.player, False)

    def update(self):
        if self.is_player_close():
            self.closed = 1
            self.open()
        else:
            self.closed = 0
            self.close()


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
