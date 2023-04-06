import pygame
import math
import renderer


class GameMap:
    def __init__(self, screen, width, height, vector, scale):
        self.screen = screen
        self.width = width
        self.height = height
        self.vector = vector
        self.scale = scale
        self.bg = pygame.Surface((self.width * self.scale, self.height * self.scale))
        self.bg.fill((41, 39, 68))
        self.objects = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.keys = pygame.key.get_pressed()

    def add_object(self, obj):
        self.objects.add(obj)

    def add_player(self, pla):
        self.player = pygame.sprite.GroupSingle(pla)

    def update(self):
        self.keys = pygame.key.get_pressed()
        for obj in self.objects.sprites():
            obj.update()
        self.player.sprite.update()

    def draw(self):
        self.screen.blit(self.bg, (self.vector[0], self.vector[1]))
        self.objects.draw(self.screen)
        self.player.sprite.draw()


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


class Box(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "opaque"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = renderer.hex_to_rgb("#3F3734") + [122]
        # self.color = [168, 168, 168, 255]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass


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


class Glass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "semitransparent"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = renderer.hex_to_rgb("#1c319f") + [122]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass


class RedGlass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "semitransparent"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = renderer.hex_to_rgb("#aa319f") + [50]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
        pass


class GreenGlass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "semitransparent"
        self.image = pygame.Surface((self.width_scaled, self.height_scaled))
        self.color = renderer.hex_to_rgb("#1caa9f") + [50]
        # self.color = [136.0, 227.0, 247.0, 122]
        self.image.fill(self.color)
        self.rect = self.image.get_rect(
            topleft=(self.x_scaled, self.y_scaled))

    def update(self):
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

        # Check speed modifiers
        if self.game_map.keys[pygame.K_LSHIFT]:
            self.speed = self.speed_sprint
            self.speed_scaled = self.speed_sprint_scaled
        if self.game_map.keys[pygame.K_LCTRL]:
            self.speed = self.speed_crouch
            self.speed_scaled = self.speed_crouch_scaled

        # Check movement keys
        if self.game_map.keys[pygame.K_w] or pygame.mouse.get_pressed()[0]:
            vector_moved[0] += self.vectors[0][0]
            vector_moved[1] += self.vectors[0][1]
        if self.game_map.keys[pygame.K_s] or pygame.mouse.get_pressed()[2]:
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

    def update(self):
        self.player_input()

    def draw(self):
        self.game_map.screen.blit(self.image, self.image_rect)
