import json

from editor.player import EditorPlayer


class EditorCollection:
    def __init__(self, game_map, screen, config_loader):
        self.editor_players = []
        self.game_map = game_map
        self.screen = screen
        self.config_loader = config_loader
        self.config_loader.load_config()
        self.current_index = None

    def check_type(self):
        player = self.current_player()
        if player:
            player.check_type()

    def current_player(self):
        if self.current_index is not None:
            return self.editor_players[self.current_index]

    def get_current_player_name(self):
        if self.current_index is not None:
            return self.editor_players[self.current_index].type.name
        return ""

    # def insert_players(self, players):
    #     for player in players:
    #         self.game_map.add_object(player)
    #         self.editor_players.append(player)

    def new_player(self, x, y, width=5, height=5, block_type="Box"):
        self.save_current_player()
        player = EditorPlayer(self.screen, self.game_map, x, y,
                              width, height, block_type)
        self.game_map.set_player(player)
        self.current_index = len(self.editor_players)
        self.editor_players.append(player)

    def choose_player(self, index):
        self.save_current_player()
        self.current_index = index
        player = self.editor_players[self.current_index]
        player.is_active = True
        self.game_map.remove_object(player)
        self.game_map.set_player(player)

    def delete_current_player(self):
        current = self.current_player()
        if current:
            self.game_map.remove_player(current)
            del self.editor_players[self.current_index]
            self.current_index = None

    def save_current_player(self):
        current = self.current_player()
        if current:
            current.is_active = False
            self.game_map.add_object(current)
            self.game_map.remove_player(current)
            self.current_index = None

    def check_click(self, mouse):
        for i, player in enumerate(self.editor_players):
            if player.rect.collidepoint(mouse):
                self.choose_player(i)
                return
        self.new_player(mouse[0], mouse[1])

    def insert_border(self, objects):
        width = self.config_loader.width
        height = self.config_loader.height

        border = [
            {
                "width": width,
                "height": width / 100,
                "x": 0,
                "y": 0,
                "type": "Border"
             },
            {
                "width": width,
                "height": width / 100,
                "x": 0,
                "y": height - width / 100,
                "type": "Box"
            },
            {
                "width": width / 100,
                "height": height - 2 * width / 100,
                "x": 0,
                "y": width / 100,
                "type": "Box"
            },
            {
                "width": width / 100,
                "height": height - 2 * width / 100,
                "x": width - width / 100,
                "y": width / 100,
                "type": "Box"
            },
            ]

        objects.extend(border)

    def player_zero(self, objects):
        width = self.config_loader.width
        height = self.config_loader.height

        player = {"width": width / 100,
                  "height": width / 100,
                  "x": width / 2 - width / 200,
                  "y": height / 2 - width / 200,
                  "type": "Player"}

        objects.append(player)

    def to_json(self, filename):
        players = self.editor_players
        objects = [pla.to_dict() for pla in players if not pla.is_active]
        if not objects:
            objects = []
        self.insert_border(objects)

        with open(filename, "w") as f:
            json.dump(objects, f, indent=2)
