import pygame
from src.pathfinder import *


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
        self.state = "playing"
        self.objectives = pygame.sprite.Group()
        self.pathfinder = Pathfinder()

    def add_objective(self, obj):
        self.objectives.add(obj)

    def remove_objective(self, obj):
        self.objectives.remove(obj)

    def add_object(self, obj):
        self.objects.add(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

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

    def set_player(self, pla):
        self.player = pygame.sprite.GroupSingle(pla)

    def remove_player(self, pla):
        self.player.remove(pla)

    def update_pathfinder(self):
        self.pathfinder.change_objects(self.objects)
        self.pathfinder.build_graph()

    def update(self):
        self.keys = pygame.key.get_pressed()
        for obj in self.objects.sprites():
            obj.update()
        for enemy in self.enemies.sprites():
            enemy.update()
        for projectile in self.projectiles.sprites():
            projectile.update()
        for objective in self.objectives.sprites():
            objective.update()
        if self.player:
            self.player.sprite.update()

    def draw(self):
        self.screen.blit(self.bg, (self.vector[0], self.vector[1]))
        self.objects.draw(self.screen)
        self.enemies.draw(self.screen)
        self.projectiles.draw(self.screen)
        if self.player:
            self.player.sprite.draw()

    def all_objectives_met(self):
        if not self.objectives.sprites():
            return False

        for obj in self.objectives.sprites():
            if not obj.passed:
                return False
        return True
