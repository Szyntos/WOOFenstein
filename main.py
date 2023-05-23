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

    def _map_width_scaled(self):
        return self.map_width * self.scale

    def _map_height_scaled(self):
        return self.map_height * self.scale

    def _render_width(self):
        return 2 * self._map_width_scaled()

    def _render_height(self):
        return self._map_height_scaled()

    def _window_width(self):
        return 0 * self._map_width_scaled() + self._render_width()

    def _window_height(self):
        return max(self._render_height(), self._map_height_scaled())

    def _get_vector(self):
        return [self._render_width() - self._map_width_scaled() * self.map_scale, 0]

    def get_screen(self) -> pygame.Surface | pygame.SurfaceType:
        mode = (self._window_width(), self._window_height())
        return pygame.display.set_mode(mode)

    def create_map(self, screen: pygame.Surface | pygame.SurfaceType):
        self.map = GameMap(screen, self._map_width_scaled(), self._map_height_scaled(),
                           self._get_vector(), self.map_scale)

    def populate_map(self, screen: pygame.Surface | pygame.SurfaceType):
        with open(self.map_config, "r") as f:
            objects = json.load(f)

        block_constructors = get_block_constructors()
        for obj in objects:
            width = obj["width"] * self.scale
            height = obj["height"] * self.scale
            x = obj["x"] * self.scale
            y = obj["y"] * self.scale
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
        return Gui(self.map, self._window_width(), self._window_height(),
                   self.scale, self.map_width, self.map_height)

    def setup_pathfinder(self):
        self.map.pathfinder.leeway = self.player_width / 2
        self.map.update_pathfinder()


class Client:
    def __init__(self):
        pygame.init()

        self.config_loader = ConfigLoader("config.json", "map2.json")
        self.config_loader.load_config()

        self.screen = self.config_loader.get_screen()
        # infoObject = pygame.display.Info()
        # self.screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
        # self.actual_screen = self.config_loader.get_screen()

        self.config_loader.create_map(self.screen)
        self.config_loader.populate_map(self.screen)
        self.map = self.config_loader.map
        self.renderer = self.config_loader.create_renderer()
        self.map.renderer = self.renderer
        self.gui = self.config_loader.create_gui()
        self.config_loader.setup_pathfinder()

        self.font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 20)
        self.clock = pygame.time.Clock()

        self.mouse_sensitivity = 1.5

        pygame.display.set_caption("WOOFenstien")
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def check_events(self, mouse_move, debug_var):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEMOTION:
                mouse_move[0] = self.mouse_sensitivity * event.rel[0]
                mouse_move[1] = self.mouse_sensitivity * event.rel[1]
            if event.type == pygame.MOUSEWHEEL:
                debug_var += event.y
                debug_var = max(1, debug_var)
        return debug_var

    def check_state(self):
        if self.map.state == "playing":
            self.renderer.render()
            self.gui.draw_gui()
            self.map.draw()
            self.map.update()
            self.renderer.draw_rays()
        elif self.map.state == "over":
            self.gui.draw_game_over()
        else:
            self.gui.draw_won()

    def show_fps(self):
        fps = int(self.clock.get_fps())
        text = self.font.render(str(fps), True, "black")
        self.screen.blit(text, (10, 10))

    def sprite_click(self, debug_var):
        if len(self.map.enemies.sprites()):
            if pygame.mouse.get_pressed()[1]:
                if debug_var:
                    self.map.enemies.sprites()[0].click = 1
                    # game_map.enemies.sprites()[0].click %= 2
                else:
                    self.map.enemies.sprites()[0].click = 0
                debug_var = 0
            else:
                debug_var = 1
                self.map.enemies.sprites()[0].click = 0
        return debug_var

    def run(self):
        # start = time.time()
        debug_i = 70
        debug_f = 1
        while True:
            # if time.time() - start > 20:
            #     pygame.quit()
            #     exit()

            mouse_move = [0, 0]
            debug_i = self.check_events(mouse_move, debug_i)

            debug_f = self.sprite_click(debug_f)

            if self.map.all_objectives_met():
                self.map.state = "won"

            # renderer.set_ray_count(i)
            sprite = self.map.player.sprite
            sprite.rotate_mouse(mouse_move)
            self.renderer.generate_rays(sprite.x + sprite.width / 2,
                                        sprite.y + sprite.height / 2,
                                        sprite.orientation)

            self.check_state()

            # self.renderer.draw_visible_edges(sprite.x + sprite.width / 2,
            #                             sprite.y + sprite.height / 2,
            #                             sprite.orientation)

            # Show FPS
            self.show_fps()

            pygame.display.update()
            self.clock.tick(40)


if __name__ == "__main__":
    client = Client()
    client.run()
