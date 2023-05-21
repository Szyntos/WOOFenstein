from map import *
from renderer import *
from imports import *
from gui import *

# Setting map constants
scale = 0.75

MAP_WIDTH = 900
MAP_HEIGHT = 900
RAY_COUNT = 70  # Actual number of rays is 2*RAY_COUNT-1
FOV = 110
PLAYER_WIDTH = 10

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

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("WOOFenstien")
font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 20)
clock = pygame.time.Clock()
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

map_scale = 0.4
game_map = GameMap(screen, MAP_WIDTH, MAP_HEIGHT, [RENDER_WIDTH - MAP_WIDTH * map_scale, 0], map_scale)
renderer = Renderer(game_map, RENDER_WIDTH, FOV, RAY_COUNT)
gui = Gui(game_map, WINDOW_WIDTH, WINDOW_HEIGHT)
game_map.renderer = renderer

# Adding objects to the map
game_map.add_object(Border(screen, game_map, MAP_WIDTH, 10, 0, 0))
game_map.add_object(Border(screen, game_map, MAP_WIDTH, 10, 0, MAP_HEIGHT - 10))
game_map.add_object(Border(screen, game_map, 10, MAP_HEIGHT - 20, 0, 10))
game_map.add_object(Border(screen, game_map, 10, MAP_HEIGHT - 20, MAP_WIDTH - 10, 10))
#


# MAZE
w = -20
h = -50
game_map.add_object(GreenGlass(screen, game_map, 10, 560, 100 + w, 100 + h))
game_map.add_object(GreenGlass(screen, game_map, 10, 550, 650 + w, 110 + h))
game_map.add_object(GreenGlass(screen, game_map, 110, 10, 430 + w, 540 + h))
game_map.add_object(GreenGlass(screen, game_map, 110, 10, 320 + w, 320 + h))
game_map.add_object(GreenGlass(screen, game_map, 10, 100, 430 + w, 550 + h))
game_map.add_object(GreenGlass(screen, game_map, 10, 120, 430 + w, 320 + h))
game_map.add_object(GreenGlass(screen, game_map, 90, 10, 0, 300 + h))
game_map.add_object(GreenGlass(screen, game_map, 90, 10, 640, 300 + h))

game_map.add_object(GreenGlass(screen, game_map, 220, 10, 430 + w, 650 + h))
game_map.add_object(GreenGlass(screen, game_map, 110, 10, 540 + w, 430 + h))
game_map.add_object(GreenGlass(screen, game_map, 330, 10, 210 + w, 210 + h))
game_map.add_object(GreenGlass(screen, game_map, 230, 10, 110 + w, 100 + h))

game_map.add_object(GreenGlass(screen, game_map, 230, 10, 430 + w, 100 + h))
game_map.add_object(GreenGlass(screen, game_map, 220, 10, 110 + w, 650 + h))
game_map.add_object(GreenGlass(screen, game_map, 110, 10, 320 + w, 430 + h))
game_map.add_object(GreenGlass(screen, game_map, 10, 210, 320 + w, 440 + h))
game_map.add_object(GreenGlass(screen, game_map, 10, 220, 540 + w, 210 + h))
game_map.add_object(GreenGlass(screen, game_map, 10, 330, 210 + w, 210 + h))

# game_map.add_object(Box(screen, game_map, 100, 10, 100, 100))
# game_map.add_object(Box(screen, game_map, 10, 50, 300, 100))
# #
# game_map.add_object(Box(screen, game_map, 10, 10, 300, 300))
# game_map.add_object(GreenGlass(screen, game_map, 10, 100, 200, 100))
# game_map.add_object(GreenGlass(screen, game_map, 100, 100, 50, 350))
# game_map.add_object(Glass(screen, game_map, 100, 10, 350, 350))
# game_map.add_object(Box(screen, game_map, 10, 50, 400, 390))
# game_map.add_object(RedGlass(screen, game_map, 10, 100, 150, 120))
#
# game_map.add_object(Glass(screen, game_map, 5, 100, 550, 100))
# game_map.add_object(GreenGlass(screen, game_map, 5, 100, 540, 100))
# game_map.add_object(RedGlass(screen, game_map, 5, 100, 530, 100))

# Adding enemy to the map
game_map.add_enemy(Enemy(screen, game_map, PLAYER_WIDTH - 1, PLAYER_WIDTH - 1, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))
# game_map.add_enemy(Enemy(screen, game_map, 10, 10, MAP_WIDTH // 2, MAP_HEIGHT // 2))

# Adding player to the map
game_map.add_player(
    Player(screen, game_map, PLAYER_WIDTH + 2, PLAYER_WIDTH + 2, MAP_WIDTH // 2, MAP_HEIGHT // 2 + 200))
# game_map.add_player(Player(screen, game_map, 5, 5, 555, 150, 90))
game_map.pathfinder.leeway = PLAYER_WIDTH / 2
game_map.pathfinder.change_objects(game_map.objects)
game_map.pathfinder.build_graph()

# start = time.time()
i = 70
f = 1
while True:
    # if time.time() - start > 20:
    #     pygame.quit()
    #     exit()

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
            i = max(1, i)
    if len(game_map.enemies.sprites()):
        if pygame.mouse.get_pressed()[1]:
            if f:
                game_map.enemies.sprites()[0].click = 1
                # game_map.enemies.sprites()[0].click %= 2
            else:
                game_map.enemies.sprites()[0].click = 0
            f = 0
        else:
            f = 1
            game_map.enemies.sprites()[0].click = 0
    # renderer.set_ray_count(i)
    game_map.player.sprite.rotate_mouse(mouse_move)
    # shortest = (game_map.pathfinder.find_shortest([game_map.player.sprite.x, game_map.player.sprite.y],
    #                                               [game_map.enemies.sprites()[0].x, game_map.enemies.sprites()[0].y]))

    renderer.generate_rays(game_map.player.sprite.x + game_map.player.sprite.width / 2,
                           game_map.player.sprite.y + game_map.player.sprite.height / 2,
                           game_map.player.sprite.orientation)
    renderer.render()
    gui.draw_gui()
    game_map.draw()
    game_map.update()
    # draw_path(shortest, game_map)
    # renderer.draw_rays()
    # renderer.draw_visible_edges(game_map.player.sprite.x + game_map.player.sprite.width / 2,
    #                             game_map.player.sprite.y + game_map.player.sprite.height / 2,
    #                             game_map.player.sprite.orientation)

    # Show FPS
    text = font.render(str(int(clock.get_fps())), True, "black")
    screen.blit(text, (10, 10))

    pygame.display.update()
    clock.tick(60)
