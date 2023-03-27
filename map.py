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


class Box(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((123, 123, 123))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass
        # self.rect.x += 1
        # self.x += 1


class Glass(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((123, 123, 255))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass
        # self.rect.x += 1
        # self.x += 1


class GameMap:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.bg = pygame.Surface((self.width, self.height))
        self.bg.fill("black")
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
        self.screen.blit(self.bg, (0, 0))
        self.objects.draw(self.screen)
        self.player.draw(self.screen)


class Player(GameObject):
    def __init__(self, screen, game_map, width, height, x, y):
        super().__init__(screen, game_map, width, height, x, y)
        filename = "pinkcar.png"
        self.org = pygame.Surface((self.width, self.height))
        self.org.fill((255, 255, 255))
        self.org = pygame.image.load(filename).convert()
        self.org = pygame.transform.scale(self.org, (self.width, self.height))
        self.org.set_colorkey("BLACK")

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 255, 255))
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        self.image.set_colorkey("BLACK")

        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4
        self.angular_speed = 4
        self.vectors_org = [[0, -self.speed], [0, self.speed], [-self.speed, 0], [self.speed, 0]]
        self.vectors = [[0, -self.speed], [0, self.speed], [-self.speed, 0], [self.speed, 0]]

    def move_vector(self, vec):
        self.rect.x += vec[0]
        self.x += vec[0]
        self.rect.y += vec[1]
        self.y += vec[1]

    def player_input(self):
        vector_moved = [0, 0]
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

    def rotate_vectors(self, angle):
        self.vectors = [[math.cos(-math.pi / 180 * angle) * x - math.sin(-math.pi / 180 * angle) * y,
                         math.sin(-math.pi / 180 * angle) * x + math.cos(-math.pi / 180 * angle) * y] for x, y in
                        self.vectors_org]

    def rotate(self, angle):
        rotated_image = pygame.transform.rotate(self.org, angle)
        new_rect = rotated_image.get_rect(center=self.org.get_rect(center=self.rect.center).center)
        self.image, self.rect = rotated_image, new_rect

    def collision(self):
        return pygame.sprite.spritecollideany(self, self.game_map.objects)

    def update(self):
        self.player_input()
