from sys import exit
import pygame
import json

from src.objectives import Objective
from src.blocks import get_block_constructors
from src.map import GameMap
from src.moveable import Player, Enemy
from src.renderer import Renderer
from src.gui import Gui


class ConfigLoader:
    def __init__(self, config: str, map_config: str):
        self.config = config
        self.map_config = map_config
        self.scale = None
        self.map_width = None
        self.map_height = None
        # Actual number of rays is 2*RAY_COUNT-1
        self.ray_count = None
        self.fov = None
        self.map = None
        self.map_scale = None
        self.player_width = 10
        self.enemy_width = 10

    def load_config(self):
        with open(self.config, "r") as f:
            config_data = json.load(f)
        self.scale = config_data["scale"]
        self.map_width = config_data["map width"]
        self.map_height = config_data["map height"]
        self.ray_count = config_data["ray count"]
        self.fov = config_data["fov"]
        self.map_scale = config_data["map scale"]
        self._scale_map_attributes()

    def _render_width(self):
        return 2 * self.map_width

    def _render_height(self):
        return self.map_height

    def _window_width(self):
        return 0 * self.map_width + self._render_width()

    def _window_height(self):
        return max(self._render_height(), self.map_height)

    def _scale_map_attributes(self):
        self.map_height *= self.scale
        self.map_width *= self.scale

    def _get_vector(self):
        return [self._render_width() - self.map_width * self.map_scale, 0]

    def get_screen(self) -> pygame.Surface | pygame.SurfaceType:
        mode = (self._window_width(), self._window_height())
        return pygame.display.set_mode(mode)

    def create_map(self, screen: pygame.Surface | pygame.SurfaceType):
        self.map = GameMap(screen, self.map_width, self.map_height,
                           self._get_vector(), self.map_scale)

    def populate_map(self, screen: pygame.Surface | pygame.SurfaceType):
        with open(self.map_config, "r") as f:
            objects = json.load(f)

        block_constructors = get_block_constructors()
        for obj in objects:
            width = obj["width"]
            height = obj["height"]
            x = obj["x"]
            y = obj["y"]
            if obj["type"] == "Player":
                player = Player(screen, self.map, width, height, x, y)
                self.map.set_player(player)
                self.player_width = width
            elif obj["type"] == "Enemy":
                enemy = Enemy(screen, self.map, width, height, x, y)
                self.map.add_enemy(enemy)
                self.enemy_width = width
            elif obj["type"] == "Objective":
                objective = Objective(screen, self.map, width, height, x, y)
                self.map.add_objective(objective)
            else:
                constructor = block_constructors[obj["type"]]
                block = constructor(screen, self.map, width, height, x, y)
                self.map.add_object(block)

    def create_renderer(self) -> Renderer:
        return Renderer(self.map, self._render_width(),
                        self.fov, self.ray_count)

    def create_gui(self) -> Gui:
        return Gui(self.map, self._window_width(), self._window_height())

    def setup_pathfinder(self):
        self.map.pathfinder.leeway = self.player_width / 2
        self.map.pathfinder.change_objects(self.map.objects)
        self.map.pathfinder.build_graph()


class Client:
    def __init__(self):
        self.config_loader = ConfigLoader("config.json", "map.json")
        self.config_loader.load_config()

        self.screen = self.config_loader.get_screen()

        self.config_loader.create_map(self.screen)
        self.config_loader.populate_map(self.screen)
        self.map = self.config_loader.map
        self.renderer = self.config_loader.create_renderer()
        self.map.renderer = self.renderer
        self.gui = self.config_loader.create_gui()
        self.config_loader.setup_pathfinder()

        pygame.init()
        self.font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 20)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("WOOFenstien")
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def run(self):
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
                    mouse_move = [10 * i for i in mouse_move]
                if event.type == pygame.MOUSEWHEEL:
                    i += event.y
                    i = max(1, i)
            if len(self.map.enemies.sprites()):
                if pygame.mouse.get_pressed()[1]:
                    if f:
                        self.map.enemies.sprites()[0].click = 1
                        # game_map.enemies.sprites()[0].click %= 2
                    else:
                        self.map.enemies.sprites()[0].click = 0
                    f = 0
                else:
                    f = 1
                    self.map.enemies.sprites()[0].click = 0
            if self.map.all_objectives_met():
                pygame.quit()
                exit()
            # renderer.set_ray_count(i)
            sprite = self.map.player.sprite
            sprite.rotate_mouse(mouse_move)
            self.renderer.generate_rays(sprite.x + sprite.width / 2,
                                        sprite.y + sprite.height / 2,
                                        sprite.orientation)
            self.renderer.render()
            self.gui.draw_gui()
            self.map.draw()
            self.map.update()
            self.renderer.draw_rays()
            # self.renderer.draw_visible_edges(sprite.x + sprite.width / 2,
            #                             sprite.y + sprite.height / 2,
            #                             sprite.orientation)

            # Show FPS
            fps = int(self.clock.get_fps())
            text = self.font.render(str(fps), True, "black")
            self.screen.blit(text, (10, 10))

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    client = Client()
    client.run()
