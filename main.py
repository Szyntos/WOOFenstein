from sys import exit
import pygame
import json

from src.objectives import Objective
from src.blocks import get_block_constructors
from src.map import GameMap
from src.moveable import Player, Enemy
from src.renderer import Renderer
from src.gui import Gui
from src.gui import InputBox


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
    def __init__(self, main_menu):
        pygame.init()

        self.config_loader = ConfigLoader("config.json", main_menu.map_path)
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

        self.to_main_menu = False

        self.font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 20)
        self.clock = pygame.time.Clock()

        self.mouse_sensitivity = main_menu.mouse_sensitivity

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
                    self.to_main_menu = True
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
            if self.to_main_menu:
                return
            # if time.time() - start > 20:
            #     pygame.quit()
            #     exit()

            mouse_move = [0, 0]
            debug_i = self.check_events(mouse_move, debug_i)

            debug_f = self.sprite_click(debug_f)

            if self.map.all_objectives_met():
                self.map.state = "won"

            self.renderer.set_ray_count(debug_i)
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

class Options:
    def __init__(self, main_menu):
        self.main_menu = main_menu
        pygame.init()

        self.config_loader = ConfigLoader("config.json", "demo.json")
        self.config_loader.load_config()

        self.screen = self.config_loader.get_screen()

        self.font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 20)
        self.button_font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 50)
        self.clock = pygame.time.Clock()

        self.gui = self.config_loader.create_gui()
        filename = "img/bg.jpg"
        bg = pygame.image.load(filename).convert_alpha()
        self.bg = pygame.transform.scale(bg, (self.gui.won.get_width(), self.gui.won.get_height()))

        self.mouse_sensitivity = 1.5


        self.input_box1 = InputBox(100, 100, 140, 32, "Mouse Sensitivity")
        self.input_box2 = InputBox(100, 300, 140, 32, "Map (demo / mainGame / maze)", "demo")
        self.input_boxes = [self.input_box1, self.input_box2]
        self.exit_options = False
        pygame.display.set_caption("WOOFenstien")
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

    def check_events(self, mouse_move, debug_var):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.exit_options = True

            elif event.type == pygame.MOUSEMOTION:
                mouse_move[0] = self.mouse_sensitivity * event.rel[0]
                mouse_move[1] = self.mouse_sensitivity * event.rel[1]
            for box in self.input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEWHEEL:
                debug_var += event.y
                debug_var = max(1, debug_var)
        return debug_var

    def show_fps(self):
        fps = int(self.clock.get_fps())
        text = self.font.render(str(fps), True, "black")
        self.screen.blit(text, (10, 10))

    def run(self):
        debug_i = 70

        while True:
            if self.exit_options:
                return
            self.screen.blit(self.bg, (0, 0))
            mouse_move = [0, 0]
            debug_i = self.check_events(mouse_move, debug_i)
            for box in self.input_boxes:
                box.update()
            for box in self.input_boxes:
                box.draw(self.screen)
            try:
                self.main_menu.mouse_sensitivity = float(self.input_boxes[0].text)
            except:
                pass
            try:
                self.main_menu.map_path = "maps/" + self.input_boxes[1].text.lower() + ".json"
            except:
                pass

            self.show_fps()

            pygame.display.update()
            self.clock.tick(40)

class MainMenu:
    def __init__(self):
        pygame.init()

        self.config_loader = ConfigLoader("config.json", "demo.json")
        self.config_loader.load_config()
        self.map_path = "maps/demo.json"

        self.screen = self.config_loader.get_screen()

        self.font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 20)
        self.button_font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 50)
        self.clock = pygame.time.Clock()

        self.gui = self.config_loader.create_gui()
        filename = "img/Woof.jpg"
        bg = pygame.image.load(filename).convert_alpha()
        self.bg = pygame.transform.scale(bg, (self.gui.won.get_width(), self.gui.won.get_height()))

        self.mouse_sensitivity = 1.5

        self.play_text = self.button_font.render("Play", True, "white")
        self.play_rect = self.play_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 10 * 5))
        self.options_text = self.button_font.render("Options", True, "white")
        self.options_rect = self.options_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 10 * 8))
        self.credits_text = self.button_font.render("Credits", True, "white")
        self.credits_rect = self.credits_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 10 * 9))
        self.game_play = False
        self.options = False
        self.credits = False

        self.slider_value = 1.5
        self.slider_rect = pygame.Rect(50, 500, 200, 10)
        self.slider_handle_rect = pygame.Rect(self.slider_rect.x + (self.slider_value * self.slider_rect.width) - 5,
                                              self.slider_rect.y - 5, 10, 20)

        pygame.display.set_caption("WOOFenstien")
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

    def draw_slider(self):
        # Draw slider background
        pygame.draw.rect(self.screen, "gray", self.slider_rect)

        # Draw slider handle
        pygame.draw.rect(self.screen, "black", self.slider_handle_rect)

    def update_slider(self):
        # Update slider handle position based on the slider value
        self.slider_handle_rect.x = self.slider_rect.x + (self.slider_value * self.slider_rect.width) - 5

    def check_slider_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.slider_handle_rect.collidepoint(event.pos):
                self.dragging_slider = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_slider = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            # Update slider value based on mouse position
            normalized_pos = (event.pos[0] - self.slider_rect.x) / self.slider_rect.width
            self.slider_value = max(0, min(1, normalized_pos))
            # Update the mouse sensitivity
            self.mouse_sensitivity = 0.1 + 2.9 * self.slider_value

    def check_events(self, mouse_move, debug_var, play_rect, options_rect, credits_rect):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_move[0] = self.mouse_sensitivity * event.rel[0]
                mouse_move[1] = self.mouse_sensitivity * event.rel[1]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if play_rect.collidepoint(event.pos):
                        self.game_play = True
                        # Add your play button action here
                    elif options_rect.collidepoint(event.pos):
                        self.options = True
                        # Add your options button action here
                    elif credits_rect.collidepoint(event.pos):
                        print("Credits button clicked!")
                        # Add your credits button action here

            if event.type == pygame.MOUSEWHEEL:
                debug_var += event.y
                debug_var = max(1, debug_var)
        return debug_var

    def draw_main_buttons(self):

        self.screen.blit(self.play_text, self.play_rect)

        self.screen.blit(self.options_text, self.options_rect)

        self.screen.blit(self.credits_text, self.credits_rect)


    def show_fps(self):
        fps = int(self.clock.get_fps())
        text = self.font.render(str(fps), True, "black")
        self.screen.blit(text, (10, 10))

    def run(self):
        debug_i = 70

        while True:
            self.screen.blit(self.bg, (0, 0))
            mouse_move = [0, 0]
            debug_i = self.check_events(mouse_move, debug_i, self.play_rect, self.options_rect, self.credits_rect)
            # Show FPS
            if self.game_play:
                client = Client(self)
                client.run()
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                self.game_play = False
            if self.options == True:
                options = Options(self)
                options.run()
                self.options = False
            self.draw_main_buttons()
            self.show_fps()

            pygame.display.update()
            self.clock.tick(40)


if __name__ == "__main__":
    mainMenu = MainMenu()
    mainMenu.run()
