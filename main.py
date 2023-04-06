from map import *
from sys import exit
from renderer import *
import time

pygame.init()

# Setting map constants
scale = 0.75

MAP_WIDTH = 900
MAP_HEIGHT = 900
RAY_COUNT = 90  # Actual number of rays is 2*RAY_COUNT-1
FOV = 90

RENDER_WIDTH = 2 * MAP_WIDTH
RENDER_HEIGHT = MAP_HEIGHT

WINDOW_WIDTH = 0 * MAP_WIDTH + RENDER_WIDTH
WINDOW_HEIGHT = max(RENDER_HEIGHT, MAP_HEIGHT)

MAP_WIDTH *= scale
MAP_HEIGHT *= scale
RENDER_WIDTH *= scale
RENDER_HEIGHT *= scale
WINDOW_WIDTH *= scale
WINDOW_HEIGHT *= scale

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("WOOFenstien")
font = pygame.font.Font('digital-7/digital-7.ttf', 20)

clock = pygame.time.Clock()

map_scale = 0.4
game_map = GameMap(screen, MAP_WIDTH, MAP_HEIGHT, [RENDER_WIDTH - MAP_WIDTH * map_scale, 0], map_scale)
# Adding objects to the map
game_map.add_object(Box(screen, game_map, 100, 10, 100, 100))
game_map.add_object(Box(screen, game_map, 10, 10, 100, 100))
game_map.add_object(Box(screen, game_map, 10, 50, 300, 100))
game_map.add_object(Box(screen, game_map, MAP_WIDTH, 10, 0, 0))
game_map.add_object(Box(screen, game_map, MAP_WIDTH, 10, 0, MAP_HEIGHT - 10))
game_map.add_object(RedBox(screen, game_map, 10, MAP_HEIGHT - 20, 0, 10))
game_map.add_object(Box(screen, game_map, 10, MAP_HEIGHT - 20, MAP_WIDTH - 10, 10))
game_map.add_object(RedBox(screen, game_map, 10, MAP_HEIGHT - 20, 300, 10))
game_map.add_object(Box(screen, game_map, 10, MAP_HEIGHT - 20, 300 + 30, 10))
game_map.add_object(Box(screen, game_map, 10, 10, 300, 300))
game_map.add_object(GreenGlass(screen, game_map, 10, 100, 200, 100))
game_map.add_object(GreenGlass(screen, game_map, 100, 100, 50, 350))
game_map.add_object(Glass(screen, game_map, 100, 10, 350, 350))
game_map.add_object(Box(screen, game_map, 10, 50, 400, 390))
game_map.add_object(RedGlass(screen, game_map, 10, 100, 150, 120))
game_map.add_object(Glass(screen, game_map, 5, 100, 550, 100))
game_map.add_object(GreenGlass(screen, game_map, 5, 100, 540, 100))
game_map.add_object(RedGlass(screen, game_map, 5, 100, 530, 100))
# game_map.add_object(Box(screen, game_map, 5, 5, MAP_WIDTH // 2 - 20, MAP_HEIGHT // 2 + 100))

# Adding player to the map
game_map.add_player(Player(screen, game_map, 5, 5, MAP_WIDTH // 2 - 20, MAP_HEIGHT // 2 + 200))
# game_map.add_player(Player(screen, game_map, 5, 5, 555, 150, 90))

renderer = Renderer(game_map, RENDER_WIDTH, FOV, RAY_COUNT)

pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

start = time.time()
i = 0
while True:
    # if time.time() - start > 10:
    #     pygame.quit()
    #     exit()
    # pygame.mouse.set_pos = (0, 0)
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
        if event.type == pygame.MOUSEWHEEL:
            i += event.y

    game_map.player.sprite.rotate_mouse(mouse_move)

    renderer.generate_rays(game_map.player.sprite.x + game_map.player.sprite.width / 2,
                           game_map.player.sprite.y + game_map.player.sprite.height / 2,
                           game_map.player.sprite.orientation)
    renderer.render()
    game_map.draw()
    game_map.update()
    renderer.draw_rays()
    # renderer.draw_visible_edges(game_map.player.sprite.x + game_map.player.sprite.width / 2,
    #                             game_map.player.sprite.y + game_map.player.sprite.height / 2,
    #                             game_map.player.sprite.orientation)

    # Show FPS
    text = font.render(str(int(clock.get_fps())), True, "white")
    screen.blit(text, (10, 10))

    pygame.display.update()

    clock.tick(60)
