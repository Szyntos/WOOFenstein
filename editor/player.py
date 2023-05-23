import pygame

from src.blocks import GameObject
from src.utils import hex_to_rgb


class BlockType:
    def __init__(self, block_type: str):
        self.name = block_type
        self.types = ["Box", "RedBox", "Glass", "RedGlass", "Player", "Enemy", "Objective", "Door"]

    def get_color(self):
        match self.name:
            case "Box":
                return hex_to_rgb("#3F3734") + [122]
            case "RedBox":
                return [120, 70, 70, 255]
            case "Glass":
                return hex_to_rgb("#1c319f") + [122]
            case "RedGlass":
                return hex_to_rgb("#aa319f") + [50]
            case "GreenGlass":
                return hex_to_rgb("#1caa9f") + [50]
            case "Player":
                return [255, 140, 0]
            case "Enemy":
                return [0, 0, 0]
            case "Door":
                return hex_to_rgb("#B67107") + [122]
            case "Objective":
                return [230, 230, 250]

    def _type_index(self):
        return self.types.index(self.name)

    def next(self):
        index = (self._type_index() + 1) % len(self.types)
        self.name = self.types[index]

    def previous(self):
        index = (len(self.types) + self._type_index() - 1) % len(self.types)
        self.name = self.types[index]


class EditorPlayer(GameObject):
    def __init__(self, screen, game_map, x, y, width=5, height=5, block_type="Glass"):
        super().__init__(screen, game_map, width, height, x, y)

        self.is_active = True

        self.type = BlockType(block_type)
        self.color = self.type.get_color()

        self.image = self._new_image()

        self.min_height = 5
        self.min_width = 5

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.speed = 2.5
        self.vectors = [[0, -1], [0, 1], [-1, 0], [1, 0]]

        self.resize_speed = 4
        self.resize_vectors = [[0, -1], [0, 1], [-1, 0], [1, 0]]

    def move_vector(self, vec):
        self.x += vec[0] * self.speed
        self.y += vec[1] * self.speed

        self.rect.x = self.x
        self.rect.y = self.y

    def _check_movement_keys(self, vector_moved: list[int, int]):
        keys = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
        for i, key in enumerate(keys):
            if self.game_map.keys[key]:
                vector_moved[0] += self.vectors[i][0]
                vector_moved[1] += self.vectors[i][1]

    def _set_width(self, width_delta):
        new_width = self.width + width_delta
        if not self.min_width <= new_width:
            return
        self.width = new_width
        self.rect.w = self.width

    def _set_height(self, height_delta):
        new_height = self.height + height_delta
        if not self.min_height <= new_height:
            return
        self.height = new_height
        self.rect.h = self.height

    def _new_image(self):
        image = pygame.Surface((self.width, self.height))
        self.color = self.type.get_color()
        image.fill(self.color)
        return image

    def _resize(self, resize_vector):
        width_delta = resize_vector[0] * self.resize_speed
        height_delta = resize_vector[1] * self.resize_speed
        self._set_width(width_delta)
        self._set_height(height_delta)

    def _check_resize_keys(self, vector_resized):
        keys = [pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]
        for i, key in enumerate(keys):
            if self.game_map.keys[key]:
                vector_resized[0] += self.resize_vectors[i][0]
                vector_resized[1] += self.resize_vectors[i][1]

    def check_type(self):
        if self.game_map.keys[pygame.K_PERIOD]:
            self.type.next()
        elif self.game_map.keys[pygame.K_COMMA]:
            self.type.previous()
        self.image = self._new_image()

    def player_input(self):
        vector_moved = [0, 0]
        self._check_movement_keys(vector_moved)
        self.move_vector([vector_moved[0], 0])
        self.move_vector([0, vector_moved[1]])

        vector_resized = [0, 0]
        self._check_resize_keys(vector_resized)
        self._resize(vector_resized)
        self.image = self._new_image()

    def update(self):
        if self.is_active:
            self.player_input()

    def draw(self):
        self.game_map.player.draw(self.screen)

    def to_dict(self):
        return {
            "width": (self.width/self.game_map.scale),
            "height": (self.height/self.game_map.scale),
            "x": (self.x/self.game_map.scale),
            "y": (self.y/self.game_map.scale),
            "type": self.type.name
        }
