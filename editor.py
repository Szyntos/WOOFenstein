import pygame
import json

from editor.collection import EditorCollection
from src.map import GameMap


class ConfigLoader:
    def __init__(self, config: str, map_config: str):
        self.config = config
        self.map_config = map_config
        self.scale = None
        self.width = None
        self.height = None
        self.map = None

    def load_config(self):
        with open(self.config, "r") as f:
            config_data = json.load(f)
        self.scale = config_data["scale"]
        self.width = config_data["map width"]
        self.height = config_data["map height"]

    def get_screen(self) -> pygame.Surface | pygame.SurfaceType:
        mode = (self.width, self.height)
        return pygame.display.set_mode(mode)

    def create_map(self, screen: pygame.Surface | pygame.SurfaceType):
        self.map = GameMap(screen, self.width, self.height, [0, 0], 1)


class Editor:
    def __init__(self):
        self.config_loader = ConfigLoader("config.json", "map.json")
        self.config_loader.load_config()

        self.screen = self.config_loader.get_screen()

        self.config_loader.create_map(self.screen)
        self.map = self.config_loader.map

        pygame.init()
        self.font = pygame.font.Font('digital-7/digital-7 (mono).ttf', 20)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("WOOFenstien")
        # pygame.event.set_grab(True)
        pygame.mouse.set_visible(True)

        self.collection = EditorCollection(self.map, self.screen, self.config_loader)

    def run(self):
        # start = time.time()
        i = 70
        while True:
            # if time.time() - start > 20:
            #     pygame.quit()
            #     exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                elif event.type == pygame.KEYUP:
                    self.collection.check_type()
                    if event.key == pygame.K_RETURN:
                        self.collection.save_current_player()
                    elif event.key == pygame.K_BACKSPACE:
                        self.collection.delete_current_player()
                    elif event.key == pygame.K_SPACE:
                        self.collection.to_json("map2.json")
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.collection.check_click(event.pos)

            self.map.draw()
            self.map.update()

            # Show FPS
            fps = int(self.clock.get_fps())
            name = self.collection.get_current_player_name()
            text = self.font.render(str(name), True, "white")
            self.screen.blit(text, (10, 10))

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    editor = Editor()
    editor.run()
