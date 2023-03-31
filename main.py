from map import *
from sys import exit
from renderer import *
import time
pygame.init()


scale = 0.6
MAP_WIDTH = 800
MAP_HEIGHT = 800

WIDTH_3D = 1.5*MAP_WIDTH
WIDTH = MAP_WIDTH + WIDTH_3D
HEIGHT = MAP_HEIGHT

WIDTH_3D *= scale
MAP_WIDTH *= scale
MAP_HEIGHT *= scale
WIDTH *= scale
HEIGHT *= scale

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WOOFenstien")
clock = pygame.time.Clock()

game_map = GameMap(screen, MAP_WIDTH, MAP_HEIGHT, [WIDTH_3D, 0], 1)
game_map.add_object(Box(screen, game_map, 100, 10, 100, 100))
game_map.add_object(Box(screen, game_map, 10, 50, 300, 100))
game_map.add_object(Box(screen, game_map, MAP_WIDTH, 10, 0, 0))
game_map.add_object(Box(screen, game_map, MAP_WIDTH, 10, 0, MAP_HEIGHT-10))
# game_map.add_object(Box(screen, game_map, 10, MAP_HEIGHT-20, 0, 10))
game_map.add_object(Box(screen, game_map, 10, MAP_HEIGHT-20, MAP_HEIGHT-10, 10))
game_map.add_object(Box(screen, game_map, 100, 10, 100, 100))
game_map.add_object(Box(screen, game_map, 10, 10, 300, 300))
game_map.add_object(Glass(screen, game_map, 10, 100, 200, 100))
game_map.add_object(Glass(screen, game_map, 100, 100, 50, 350))
game_map.add_object(Glass(screen, game_map, 100, 10, 350, 350))
game_map.add_object(Box(screen, game_map, 10, 50, 400, 390))
# game_map.add_object(Glass(screen, game_map, 10, 100, 150, 120))
game_map.add_player(Player(screen, game_map, 7, 10, MAP_WIDTH//2, MAP_HEIGHT//2))

renderer = Renderer(game_map, WIDTH_3D, 90, 70)
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)
while True:
    pygame.mouse.set_pos = (0, 0)
    mouse_move = (0, 0)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
        if event.type == pygame.MOUSEMOTION:
            mouse_move = event.rel

    game_map.player.sprite.rotate_mouse(mouse_move)
    game_map.draw()
    game_map.update()
    renderer.draw_rays(game_map.player.sprite.rect.centerx, game_map.player.sprite.rect.centery,
                       game_map.player.sprite.orientation)
    renderer.render()
    pygame.display.update()
    print(clock.get_fps())
    clock.tick(60)
