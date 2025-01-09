import arcade

from EnemyLogic.enemy_parameters import Enemy
from PlayerLogic.player_parameters import Player

PLAYER_MOVEMENT_SPEED = 3
TILE_SCALING = 1
TILE_SIZE = 128

PLAYER_GRAVITY = 10
ENEMY_GRAVITY = 10


class Map:
    def __init__(self):
        self.player = None
        self.enemy = None
        self.tile_map = None
        self.scene = None
        self.map_matrix = None
        self.last_press_time = None

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
            column = int(sprite.center_x // TILE_SIZE)
            row = int(
                (self.tile_map.height * self.tile_map.height - sprite.center_y)
                // TILE_SIZE
            )

            self.map_matrix[row][column] = 1

        for sprite in coins_layer:
            column = int(sprite.center_x // TILE_SIZE)
            row = int(
                (self.tile_map.height * self.tile_map.height - sprite.center_y)
                // TILE_SIZE
            )

            self.map_matrix[row][column] = 2

        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        # Creation of Player and Walls list in the base level
        self.spawn_player()

        # Creation of Enemy
        # self.spawn_enemy(300)

    def spawn_player(self):
        self.player = Player()
        self.player.player_respawn()

        self.scene.add_sprite_list("Player")
        self.scene.add_sprite("Player", self.player)
        self.player.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=self.player.current_gravity,
            walls=self.scene["Platforms"],
        )

    def change_player_gravity(self, do_change_gravity):
        if do_change_gravity:
            self.player.current_gravity = -self.player.current_gravity
            self.player.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player,
                gravity_constant=self.player.current_gravity,
                walls=self.scene["Platforms"],
            )

    def spawn_enemy(self, x_position):
        self.enemy = Enemy()
        self.enemy.spawn(300)

        self.scene.add_sprite_list("Enemy")
        self.scene.add_sprite("Enemy", self.enemy)
        self.enemy.physics_engine = arcade.PhysicsEnginePlatformer(
            self.enemy,
            gravity_constant=self.player.current_gravity,
            walls=self.scene["Platforms"],
        )

    def change_enemy_gravity(self, do_change_gravity):
        if do_change_gravity:
            self.enemy.current_gravity = -self.enemy.current_gravity
            self.enemy.physics_engine = arcade.PhysicsEnginePlatformer(
                self.enemy,
                gravity_constant=self.enemy.current_gravity,
                walls=self.scene["Platforms"],
            )

    def get_environment(self):
        player_current_x = int(self.player.center_x // TILE_SIZE)
        # Le y=0 de la matrice est en haut,alors que celui de l'écran
        # est en bas, il faut donc bidouiller un peu
        player_current_y = int(
            (self.tile_map.height * TILE_SIZE - self.player.center_y) // TILE_SIZE
        )

        radar_current_side = False
        radar_opposite_side = False
        radar_front = False

        current_gravity = self.player.current_gravity

        try:
            for i in range(player_current_y, -1, -1):
                if current_gravity > 0:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_current_side = True
                        break
                else:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_opposite_side = True
                        break

            for i in range(player_current_x, player_current_x + 2):
                if self.map_matrix[player_current_y][i] == 1:
                    radar_front = True
                    break

            for i in range(player_current_y, 7, 1):
                if current_gravity > 0:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_opposite_side = True
                        break
                else:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_current_side = True
                        break

        except Exception:
            # out of bound
            return (0, 0, 0)
        return (radar_current_side, radar_front, radar_opposite_side)
