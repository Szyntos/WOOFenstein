from imports import *
from map import *
from blocks import *


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
        self.vectors = [[(math.cos(-math.pi / 180 * orientation) * x - math.sin(-math.pi / 180 * orientation) * y),
                         (math.sin(-math.pi / 180 * orientation) * x + math.cos(-math.pi / 180 * orientation) * y)] for
                        x, y in
                        self.vectors_org]

        self.birth_time = time.time()
        self.time_alive = time_alive
        self.update()

    def collision(self):
        return pygame.sprite.spritecollideany(self, self.game_map.objects)

    def if_hit(self):
        return pygame.sprite.spritecollideany(self, self.game_map.enemies)

    def update(self):

        if self.if_hit() or time.time() - self.birth_time > self.time_alive:
            self.game_map.remove_projectile(self)
        vec = self.vectors[0]
        self.x += vec[0] * self.speed
        self.x_scaled += vec[0] * self.speed_scaled
        self.rect.x = self.x_scaled
        if self.collision():
            self.x -= vec[0] * self.speed
            self.x_scaled -= vec[0] * self.speed_scaled
            self.rect.x = self.x_scaled
            self.vectors[0][0] *= -1
        self.y += vec[1] * self.speed
        self.y_scaled += vec[1] * self.speed_scaled
        self.rect.y = self.y_scaled
        if self.collision():
            self.x -= vec[1] * self.speed
            self.x_scaled -= vec[1] * self.speed_scaled
            self.rect.x = self.x_scaled
            self.vectors[0][1] *= -1
        pass


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
        self.vectors = [[(math.cos(-math.pi / 180 * self.orientation) * x
                          - math.sin(-math.pi / 180 * self.orientation) * y),
                         (math.sin(-math.pi / 180 * self.orientation) * x
                          + math.cos(-math.pi / 180 * self.orientation) * y)] for x, y in
                        self.vectors_org]
        self.noise = PerlinNoise(octaves=3)
        self.n_i = random.random()
        self.health = 4

    def rotate_vectors(self, angle):
        self.vectors = [[(math.cos(-math.pi / 180 * angle) * x - math.sin(-math.pi / 180 * angle) * y),
                         (math.sin(-math.pi / 180 * angle) * x + math.cos(-math.pi / 180 * angle) * y)] for x, y in
                        self.vectors_org]

    def collision(self):
        return pygame.sprite.spritecollideany(self, self.game_map.objects)

    def is_shot(self):
        return pygame.sprite.spritecollideany(self, self.game_map.projectiles)

    def move(self):
        self.n_i += 0.003
        angle = (self.noise([self.n_i, self.n_i]) * 360)
        # print(angle)
        self.rotate_vectors(angle)
        vec = self.vectors[2]

        self.x += vec[0] * self.speed
        self.x_scaled += vec[0] * self.speed_scaled
        self.rect.x = self.x_scaled
        if self.collision():
            self.x -= vec[0] * self.speed
            self.x_scaled -= vec[0] * self.speed_scaled

            self.rect.x = self.x_scaled
            self.vectors_org[2][0] *= -1
        self.y += vec[1] * self.speed
        self.y_scaled += vec[1] * self.speed_scaled
        self.rect.y = self.y_scaled
        if self.collision():
            self.y -= vec[1] * self.speed
            self.y_scaled -= vec[1] * self.speed_scaled
            self.rect.y = self.y_scaled
            self.vectors_org[2][1] *= -1

    def update(self):
        if self.is_shot():
            self.health -= 1
            self.color = [min(255, c + 50) for c in self.color]
            self.image.fill(self.color)
            if self.health < 1:
                self.game_map.remove_enemy(self)
        self.move()
        pass


class Player(GameObject):
    def __init__(self, screen, game_map, width, height, x, y, initial_orientation=0):
        super().__init__(screen, game_map, width, height, x, y)
        filename = "P_2.png"
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

        if initial_orientation:
            self.orientation += initial_orientation
            self.rotate_vectors(self.orientation)
            self.rotate(self.orientation)
            if self.collision():
                self.orientation -= initial_orientation
                self.rotate(self.orientation)
            self.orientation = self.orientation % 360

    def move_vector(self, vec):
        self.x += vec[0] * self.speed
        self.y += vec[1] * self.speed
        self.x_scaled += vec[0] * self.speed_scaled
        self.y_scaled += vec[1] * self.speed_scaled

        self.rect.x = self.x_scaled
        self.rect.y = self.y_scaled
        self.image_rect.center = (self.x_scaled + self.width_scaled / 2, self.y_scaled + self.height_scaled / 2)

    def player_input(self):
        vector_moved = [0, 0]
        self.speed = self.speed_walk
        self.speed_scaled = self.speed_walk_scaled

        # Shoot
        if pygame.mouse.get_pressed()[0] or self.game_map.keys[pygame.K_UP]:
            self.game_map.add_projectile(Projectile(self.game_map.screen, self.game_map,
                                                    5, 5, self.x-2.5, self.y-2.5, self.orientation, 5, 5))
        elif pygame.mouse.get_pressed()[2] or self.game_map.keys[pygame.K_DOWN]:
            if not self.flag:
                self.game_map.add_projectile(Projectile(self.game_map.screen, self.game_map,
                                                        50, 50, self.x-25, self.y-25, self.orientation, 1, 20))
            self.flag = 1
        else:
            self.flag = 0
        # Check speed modifiers
        if self.game_map.keys[pygame.K_LSHIFT]:
            self.speed = self.speed_sprint
            self.speed_scaled = self.speed_sprint_scaled
        if self.game_map.keys[pygame.K_LCTRL]:
            self.speed = self.speed_crouch
            self.speed_scaled = self.speed_crouch_scaled

        # Check movement keys
        if self.game_map.keys[pygame.K_w]:
            vector_moved[0] += self.vectors[0][0]
            vector_moved[1] += self.vectors[0][1]
        if self.game_map.keys[pygame.K_s]:
            vector_moved[0] += self.vectors[1][0]
            vector_moved[1] += self.vectors[1][1]
        if self.game_map.keys[pygame.K_a]:
            vector_moved[0] += self.vectors[2][0]
            vector_moved[1] += self.vectors[2][1]
        if self.game_map.keys[pygame.K_d]:
            vector_moved[0] += self.vectors[3][0]
            vector_moved[1] += self.vectors[3][1]

        # Normalise speed
        s = math.sqrt(vector_moved[0] ** 2 + vector_moved[1] ** 2)
        if s > 1:
            vector_moved[0] *= 1 / s
            vector_moved[1] *= 1 / s

        self.move_vector([vector_moved[0], 0])
        # Check collision in x
        if self.collision():
            self.move_vector([-vector_moved[0], 0])

        self.move_vector([0, vector_moved[1]])
        # Check collision in y
        if self.collision():
            self.move_vector([0, -vector_moved[1]])

        # Check rotating keys
        angle = 0
        if self.game_map.keys[pygame.K_RIGHT]:
            self.orientation -= self.angular_speed
            angle -= self.angular_speed
            self.rotate_vectors(self.orientation)
            self.rotate(self.orientation)
        if self.game_map.keys[pygame.K_LEFT]:
            self.orientation += self.angular_speed
            angle += self.angular_speed
            self.rotate_vectors(self.orientation)
            self.rotate(self.orientation)

        # Check rotating collision
        if self.collision():
            self.orientation -= angle
            self.rotate(self.orientation)
        self.orientation = self.orientation % 360

    def rotate_vectors(self, angle):
        self.vectors = [[(math.cos(-math.pi / 180 * angle) * x - math.sin(-math.pi / 180 * angle) * y),
                         (math.sin(-math.pi / 180 * angle) * x + math.cos(-math.pi / 180 * angle) * y)] for x, y in
                        self.vectors_org]

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
        self.rotate_vectors(self.orientation)
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
