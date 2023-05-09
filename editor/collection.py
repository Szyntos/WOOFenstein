import json

from editor.player import EditorPlayer


class EditorCollection:
    def __init__(self, game_map, screen):
        self.editor_players = []
        self.game_map = game_map
        self.screen = screen
        self.current_index = None

    def check_type(self):
        player = self.current_player()
        if player:
            player.check_type()

    def current_player(self):
        if self.current_index is not None:
            return self.editor_players[self.current_index]

    def new_player(self, x, y):
        self.save_current_player()
        player = EditorPlayer(self.screen, self.game_map, x, y)
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

    def to_json(self, filename):
        players = self.editor_players
        objects = [pla.to_dict() for pla in players if not pla.is_active]
        with open(filename, "w") as f:
            json.dump(objects, f, indent=2)
