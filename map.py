from imports import *
from utils import *
from blocks import *
from moveable import *


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
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.keys = pygame.key.get_pressed()
        self.renderer = None

    def add_object(self, obj):
        self.objects.add(obj)

    def add_enemy(self, obj):
        self.enemies.add(obj)

    def remove_enemy(self, obj):
        self.enemies.remove(obj)
        del obj

    def add_projectile(self, obj):
        self.projectiles.add(obj)

    def remove_projectile(self, obj):
        self.projectiles.remove(obj)
        del obj

    def add_player(self, pla):
        self.player = pygame.sprite.GroupSingle(pla)

    def update(self):
        self.keys = pygame.key.get_pressed()
        for obj in self.objects.sprites():
            obj.update()
        for enemy in self.enemies.sprites():
            enemy.update()
        for projectile in self.projectiles.sprites():
            projectile.update()
        self.player.sprite.update()

    def draw(self):
        self.screen.blit(self.bg, (self.vector[0], self.vector[1]))
        self.objects.draw(self.screen)
        self.enemies.draw(self.screen)
        self.projectiles.draw(self.screen)
        self.player.sprite.draw()
