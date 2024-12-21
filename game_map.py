import arcade
import time

from PlayerLogic.player_parameters import Player

TILE_SCALING = 1
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

class Map:
    def __init__(self):
        self.physics_engine = None
        self.player = None
        self.score = None
        self.enemy_bot = None
        self.tile_map = None
        self.scene = None
        self.map_matrix = None
        self.last_press_time = None
        self.player_current_gravity = 1


    def setup(self):
        # Pour éditer la map, utiliser Tiled (https://www.mapeditor.org/)
        map_name = "resources/maps/map.json"

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        platforms_layer = self.tile_map.sprite_lists["Platforms"]
        coins_layer = self.tile_map.sprite_lists["Coins"]

        self.map_matrix = [
            [0 for _ in range(self.tile_map.width)] for _ in range(self.tile_map.height)
        ]

        for sprite in platforms_layer:
            column = int(sprite.center_x // 128)
            row = int(
                (self.tile_map.height * self.tile_map.height - sprite.center_y) // 128
            )

            self.map_matrix[row][column] = 1

        for sprite in coins_layer:
            column = int(sprite.center_x // 128)
            row = int(
                (self.tile_map.height * self.tile_map.height - sprite.center_y) // 128
            )

            self.map_matrix[row][column] = 2

        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.score = 0
        # self.scene = arcade.Scene()
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Creation of Player and Walls list in the base level
        self.scene.add_sprite_list("Player")
        self.player = Player()
        self.scene.add_sprite("Player", self.player)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=self.player_current_gravity,
            walls=self.scene["Platforms"],
        )
        # Creation of Enemy and Walls list in the base level
        self.scene.add_sprite_list("Enemy")
        self.enemy_bot = None

    def get_environment(self, current_tile):
        env = []
        for i in range(0, 7):
            env.append([])
            for j in range(current_tile, current_tile + 3):
                env[i].append(self.map_matrix[i][j])

        player_x_pos = int(self.player.center_y // 128)
        # A voir sous quel format envoyer l'environnement a la qtable
        return env, player_x_pos, self.player_current_gravity