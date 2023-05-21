import math
import time
import random
from perlin_noise import PerlinNoise
import pygame

from src.blocks import GameObject
from src.utils import hex_to_rgb, approx_equals, vector_length
from src.pathfinder import *


def rotate_vector(angle: float, vectors_org: list[list[int, int]]
                  ) -> list[list[float, float]]:
    vectors = []
    alpha = -math.pi / 180 * angle
    for x, y in vectors_org:
        a = math.cos(alpha) * x - math.sin(alpha) * y
        b = math.sin(alpha) * x + math.cos(alpha) * y
        vectors.append([a, b])
    return vectors


class Projectile(GameObject):
    def __init__(self, screen, game_map, width, height, x, y, orientation, time_alive, speed):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "semitransparent"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = hex_to_rgb("#aa4422") + [120]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))
        self.orientation = orientation
        self.speed = speed
        self.speed_scaled = self.speed * self.game_map.scale
        self.vectors_org = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        self.vectors = rotate_vector(self.orientation, self.vectors_org)

        self.birth_time = time.time()
        self.time_alive = time_alive
        self.update()

    def collision(self):
        return pygame.sprite.spritecollideany(self, self.game_map.objects)

    def is_hit(self):
        return pygame.sprite.spritecollideany(self, self.game_map.enemies)

    def update(self):

        if self.is_hit() or time.time() - self.birth_time > self.time_alive or self.collision():
            self.game_map.remove_projectile(self)
        vec = self.vectors[0]
        self.x += vec[0] * self.speed
        self.x_scaled += vec[0] * self.speed_scaled
        self.rect.x = self.x_scaled
        # if self.collision():
        #     self.x -= vec[0] * self.speed
        #     self.x_scaled -= vec[0] * self.speed_scaled
        #     self.rect.x = self.x_scaled
        #     self.vectors[0][0] *= -1
        self.y += vec[1] * self.speed
        self.y_scaled += vec[1] * self.speed_scaled
        self.rect.y = self.y_scaled
        # if self.collision():
        #     self.x -= vec[1] * self.speed
        #     self.x_scaled -= vec[1] * self.speed_scaled
        #     self.rect.x = self.x_scaled
        #     self.vectors[0][1] *= -1


class Enemy(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "opaque"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = hex_to_rgb("#aa0000") + [255]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))
        self.speed = 1.5
        self.speed_scaled = self.speed * self.game_map.scale
        self.vectors_org = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        self.orientation = random.random() * 360
        self.vectors = rotate_vector(self.orientation, self.vectors_org)

        self.noise = PerlinNoise(octaves=3)
        self.n_i = random.random()
        self.health = 10
        self.state = "idle"
        self.path = [self.x, self.y]
        self.path_state = 0
        self.path_vector = [1, 0]
        self.path_length = 0
        self.click = 0
        self.travelled_distance = 0

    def collision(self):
        return pygame.sprite.spritecollideany(self, self.game_map.objects)

    def is_shot(self):
        return pygame.sprite.spritecollideany(self, self.game_map.projectiles)

    def path_to_player(self):
        # print(self.x, self.y,self.width / 2, self.game_map.player.sprite.x, self.game_map.player.sprite.y,
        # self.game_map.player.sprite.width / 2, [self.x + self.width / 2, self.y + self.height / 2],
        # [self.game_map.player.sprite.x + self.game_map.player.sprite.width / 2, self.game_map.player.sprite.y +
        # self.game_map.player.sprite.height / 2])
        return self.game_map.pathfinder.find_shortest([self.x + self.width / 2, self.y + self.height / 2],
                                                      [self.game_map.player.sprite.x +
                                                       self.game_map.player.sprite.width / 2,
                                                       self.game_map.player.sprite.y +
                                                       self.game_map.player.sprite.height / 2])

    def switch_states(self):
        if self.state == "idle":
            self.path = self.path_to_player()
            self.path_length = get_path_length(self.path)
            # print(self.path_length)
            self.path_state = 0
            self.travelled_distance = 0
            self.state = "attack"
        else:
            self.state = "idle"

    def follow_path(self):
        draw_path(self.path, self.game_map)
        if self.travelled_distance - 100 > self.path_length:
            self.switch_states()
            return
        # print(self.travelled_distance, self.path_length)
        if (approx_equals(self.x + self.width / 2, self.path[self.path_state].x, 2) and
                approx_equals(self.y + self.height / 2, self.path[self.path_state].y, 2)):
            self.path_state += 1
            if self.path_state == len(self.path):
                self.switch_states()
                return
            self.path_vector = [self.path[self.path_state].x - self.x - self.width / 2,
                                self.path[self.path_state].y - self.y - self.height / 2]
            l = vector_length(self.path_vector)
            self.path_vector = [i / l for i in self.path_vector]

    def move(self):
        if self.state == "idle":
            self.n_i += 0.003
            angle = (self.noise([self.n_i, self.n_i]) * 360)
            # print(angle)
            self.vectors = rotate_vector(angle, self.vectors_org)
            vec = self.vectors[2]
            # vec = [0, 0]
        else:
            self.follow_path()
            vec = self.path_vector
            # print(vec)
            # print(self.path_to_player())
        vector_moved = [0, 0]

        self.x += vec[0] * self.speed
        vector_moved[0] += vec[0] * self.speed
        self.x_scaled += vec[0] * self.speed_scaled
        self.rect.x = self.x_scaled
        if self.collision():
            self.x -= vec[0] * self.speed
            self.x_scaled -= vec[0] * self.speed_scaled

            self.rect.x = self.x_scaled
            self.vectors_org[2][0] *= -1
        self.y += vec[1] * self.speed
        vector_moved[1] += vec[1] * self.speed
        self.y_scaled += vec[1] * self.speed_scaled
        self.rect.y = self.y_scaled
        if self.collision():
            self.y -= vec[1] * self.speed
            self.y_scaled -= vec[1] * self.speed_scaled
            self.rect.y = self.y_scaled
            self.vectors_org[2][1] *= -1
        self.travelled_distance += vector_length(vector_moved)

    def update(self):
        if self.click:
            self.switch_states()
        if self.is_shot():
            self.switch_states()
            self.health -= 1
            self.color = [min(255, c + 50) for c in self.color]
            self.image.fill(self.color)
            if self.health < 1:
                self.game_map.remove_enemy(self)
        self.move()


class Player(GameObject):
    def _set_initial_orientation(self, initial_orientation: float):
        if initial_orientation:
            self.orientation += initial_orientation
            self.vectors = rotate_vector(self.orientation, self.vectors_org)
            self.rotate(self.orientation)
            if self.collision():
                self.orientation -= initial_orientation
                self.rotate(self.orientation)
            self.orientation = self.orientation % 360

    def __init__(self, screen, game_map, width, height, x, y, initial_orientation=0):
        super().__init__(screen, game_map, width, height, x, y)
        filename = "./img/P_2.png"
        # Original image, used to rotate the sprite
        self.org = pygame.Surface((self.width_scaled, self.height_scaled))
        self.org.fill((255, 255, 255))
        self.org = pygame.image.load(filename).convert()
        self.org = pygame.transform.scale(self.org,
                                          (self.width_scaled, self.height_scaled))
        self.org.set_colorkey("BLACK")
        # Actual image drawn to the screen
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.image.fill((255, 255, 255))
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image,
                                            (self.width_scaled, self.height_scaled))
        self.image.set_colorkey("BLACK")
        # Rect used for drawing the rotated image to the screen
        self.image_rect = self.image.get_rect(topleft=(self.x_scaled, self.y_scaled))
        # Rect used for collision checking
        self.rect = self.image.get_rect(topleft=(self.x_scaled, self.y_scaled))

        self.health = 10

        self.speed_walk = 2.5
        self.speed_sprint = 2 * self.speed_walk
        self.speed_crouch = 0.25 * self.speed_walk

        self.speed_walk_scaled = self.speed_walk * self.game_map.scale
        self.speed_sprint_scaled = self.speed_sprint * self.game_map.scale
        self.speed_crouch_scaled = self.speed_crouch * self.game_map.scale

        self.speed = self.speed_walk
        self.speed_scaled = self.speed * self.game_map.scale

        self.angular_speed = 1.5

        self.vectors_org = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        self.vectors = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        self.flag = 0

        self._set_initial_orientation(initial_orientation)

    def move_vector(self, vec):
        self.x += vec[0] * self.speed
        self.y += vec[1] * self.speed
        self.x_scaled += vec[0] * self.speed_scaled
        self.y_scaled += vec[1] * self.speed_scaled

        self.rect.x = self.x_scaled
        self.rect.y = self.y_scaled
        self.image_rect.center = (self.x_scaled + self.width_scaled / 2, self.y_scaled + self.height_scaled / 2)

    def _check_shoot(self):
        if pygame.mouse.get_pressed()[0] or self.game_map.keys[pygame.K_UP]:
            self.game_map.add_projectile(Projectile(self.game_map.screen, self.game_map,
                                                    5, 5, self.x + self.width / 2 - 2.5,
                                                    self.y + self.height / 2 - 2.5,
                                                    self.orientation, 3, 10))
        elif pygame.mouse.get_pressed()[2] or self.game_map.keys[pygame.K_DOWN]:
            if not self.flag:
                self.game_map.add_projectile(Projectile(self.game_map.screen, self.game_map,
                                                        50, 50, self.x + self.width / 2 - 25,
                                                        self.y + self.height / 2 - 25,
                                                        self.orientation, 1, 20))
            self.flag = 1
        else:
            self.flag = 0

    def _check_speed_modifiers(self):
        if self.game_map.keys[pygame.K_LSHIFT]:
            self.speed = self.speed_sprint
            self.speed_scaled = self.speed_sprint_scaled
        if self.game_map.keys[pygame.K_LCTRL]:
            self.speed = self.speed_crouch
            self.speed_scaled = self.speed_crouch_scaled

    def _check_movement_keys(self, vector_moved: list[int, int]):
        keys = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
        for i, key in enumerate(keys):
            if self.game_map.keys[key]:
                vector_moved[0] += self.vectors[i][0]
                vector_moved[1] += self.vectors[i][1]

    def _normalise_speed(self, vector_moved: list[int, int]):
        s = math.sqrt(vector_moved[0] ** 2 + vector_moved[1] ** 2)
        if s > 1:
            vector_moved[0] *= 1 / s
            vector_moved[1] *= 1 / s

    def _move_x(self, vector_moved: list[int, int]):
        self.move_vector([vector_moved[0], 0])
        # Check collision in x
        if self.collision():
            self.move_vector([-vector_moved[0], 0])

    def _move_y(self, vector_moved: list[int, int]):
        self.move_vector([0, vector_moved[1]])
        # Check collision in y
        if self.collision():
            self.move_vector([0, -vector_moved[1]])

    def _check_rotating_keys(self) -> float:
        angle = 0
        if self.game_map.keys[pygame.K_RIGHT]:
            self.orientation -= self.angular_speed
            angle -= self.angular_speed
            self.vectors = rotate_vector(self.orientation, self.vectors_org)
            self.rotate(self.orientation)
        if self.game_map.keys[pygame.K_LEFT]:
            self.orientation += self.angular_speed
            angle += self.angular_speed
            self.vectors = rotate_vector(self.orientation, self.vectors_org)
            self.rotate(self.orientation)
        return angle

    def _check_rotating_collision(self, angle: float):
        if self.collision():
            self.orientation -= angle
            self.rotate(self.orientation)
        self.orientation = self.orientation % 360

    def player_input(self):
        vector_moved = [0, 0]
        self.speed = self.speed_walk
        self.speed_scaled = self.speed_walk_scaled
        self._check_shoot()
        self._check_speed_modifiers()
        self._check_movement_keys(vector_moved)
        self._normalise_speed(vector_moved)
        self._move_x(vector_moved)
        self._move_y(vector_moved)
        angle = self._check_rotating_keys()
        self._check_rotating_collision(angle)

    def rotate(self, angle):
        rotated_image = pygame.transform.rotate(self.org, angle)
        new_rect = rotated_image.get_rect(center=self.org.get_rect(topleft=self.org.get_rect().topleft).center)
        new_rect.center = (self.x_scaled + self.width_scaled / 2, self.y_scaled + self.height_scaled / 2)
        self.image_rect = new_rect
        self.image = rotated_image

    def rotate_mouse(self, mouse_move, sensitivity=1):
        angle = 0
        self.orientation -= mouse_move[0] / 10 * sensitivity
        angle -= mouse_move[0] / 10 * sensitivity
        self.vectors = rotate_vector(self.orientation, self.vectors_org)
        self.rotate(self.orientation)
        if self.collision():
            self.orientation -= angle
            self.rotate(self.orientation)
        self.orientation = self.orientation % 360

    def collision(self):
        return pygame.sprite.spritecollideany(self, self.game_map.objects)

    def is_killed(self):
        return pygame.sprite.spritecollideany(self, self.game_map.enemies)

    def update(self):
        if self.is_killed():
            if self.game_map.renderer:
                self.game_map.renderer.over = 1
        self.player_input()

    def draw(self):
        self.game_map.screen.blit(self.image, self.image_rect)
