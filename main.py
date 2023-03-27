from map import *
from sys import exit
import time
pygame.init()

WIDTH = 1000
HEIGHT = 1000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WOOFenstien")
clock = pygame.time.Clock()

game_map = GameMap(screen, WIDTH, HEIGHT)
game_map.add_object(Box(screen, game_map, 100, 10, 100, 100))
game_map.add_object(Glass(screen, game_map, 10, 100, 200, 100))
game_map.add_player(Player(screen, game_map, 50, 75, WIDTH//2, HEIGHT//2))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    game_map.draw()
    game_map.update()
    pygame.display.update()
    clock.tick(60)
