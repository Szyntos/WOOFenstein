import pygame, math


class GameObject(pygame.sprite.Sprite):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__()
        self.screen = screen
        self.game_map = game_map
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.orientation = 0
        self.type = None


class Box(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "Box"
        self.image = pygame.Surface((self.width * self.game_map.scale, self.height * self.game_map.scale))
        self.image.fill((123, 123, 123))
        self.rect = self.image.get_rect(
            topleft=(
                x * self.game_map.scale + self.game_map.vector[0], y * self.game_map.scale + self.game_map.vector[1]))

    def update(self):
        pass
        # self.rect.x += 1
        # self.x += 1


class Glass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.type = "Glass"
        self.image = pygame.Surface((self.width * self.game_map.scale, self.height * self.game_map.scale))
        self.image.fill((123, 123, 255))
        self.rect = self.image.get_rect(topleft=(
            x * self.game_map.scale + self.game_map.vector[0], y * self.game_map.scale + self.game_map.vector[1]))

    def update(self):
        pass
        # self.rect.x += 1
        # self.x += 1


class GameMap:
    def __init__(self, screen, width, height, vector, scale):
        self.screen = screen
        self.width = width
        self.height = height
        self.vector = vector
        self.scale = scale
        # self.bg = pygame.Surface((self.width * self.scale, self.height * self.scale))
        self.bg = pygame.Surface((10000, 10000))

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
        # self.screen.blit(self.bg, (self.vector[0], self.vector[1]))
        self.screen.blit(self.bg, (0, 0))
        self.objects.draw(self.screen)
        self.player.draw(self.screen)


class Player(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        filename = "P_2.png"
        self.org = pygame.Surface((self.width * self.game_map.scale, self.height * self.game_map.scale))
        self.org.fill((255, 255, 255))
        self.org = pygame.image.load(filename).convert()
        self.org = pygame.transform.scale(self.org,
                                          (self.width * self.game_map.scale, self.height * self.game_map.scale))
        self.org.set_colorkey("BLACK")

        self.image = pygame.Surface((self.width * self.game_map.scale, self.height * self.game_map.scale))
        self.image.fill((255, 255, 255))
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image,
                                            (self.width * self.game_map.scale, self.height * self.game_map.scale))

        self.image.set_colorkey("BLACK")

        self.rect = self.image.get_rect(topleft=(
            x * self.game_map.scale + self.game_map.vector[0], y * self.game_map.scale + self.game_map.vector[1]))
        self.x = x * self.game_map.scale + self.game_map.vector[0]
        self.y = y * self.game_map.scale + self.game_map.vector[1]
        self.speed_walk = 1
        self.speed_sprint = 2 * self.speed_walk
        self.speed_crouch = 0.5 * self.speed_walk
        self.speed_walk *= self.game_map.scale
        self.speed_sprint *= self.game_map.scale
        self.speed = self.speed_walk
        self.angular_speed = 1.5
        self.vectors_org = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        self.vectors = [[0, -1], [0, 1], [-1, 0], [1, 0]]

    def move_vector(self, vec):
        self.x += vec[0] * self.speed
        self.y += vec[1] * self.speed
        self.rect.x = self.x
        self.rect.y = self.y

    def player_input(self):
        # print(self.orientation)
        vector_moved = [0, 0]
        self.speed = self.speed_walk
        if self.game_map.keys[pygame.K_LSHIFT]:
            self.speed = self.speed_sprint
        if self.game_map.keys[pygame.K_LCTRL]:
            self.speed = self.speed_crouch
        if self.game_map.keys[pygame.K_w]:
            self.move_vector(self.vectors[0])
            vector_moved[0] += self.vectors[0][0]
            vector_moved[1] += self.vectors[0][1]

        if self.game_map.keys[pygame.K_s]:
            self.move_vector(self.vectors[1])
            vector_moved[0] += self.vectors[1][0]
            vector_moved[1] += self.vectors[1][1]

        if self.collision():
            self.move_vector([-x for x in vector_moved])

        vector_moved = [0, 0]
        if self.game_map.keys[pygame.K_a]:
            self.move_vector(self.vectors[2])
            vector_moved[0] += self.vectors[2][0]
            vector_moved[1] += self.vectors[2][1]

        if self.game_map.keys[pygame.K_d]:
            self.move_vector(self.vectors[3])
            vector_moved[0] += self.vectors[3][0]
            vector_moved[1] += self.vectors[3][1]

        if self.collision():
            self.move_vector([-x for x in vector_moved])

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
        new_rect = rotated_image.get_rect(center=self.org.get_rect(center=self.rect.center).center)
        self.x -= self.rect.x - new_rect.x
        self.y -= self.rect.y - new_rect.y
        self.image, self.rect = rotated_image, new_rect

    def rotate_mouse(self, mouse_move):
        angle = 0
        self.orientation -= mouse_move[0]/10
        angle -= mouse_move[0]/10
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
