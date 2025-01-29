import arcade

from EnemyLogic.enemy_parameters import Enemy
from PlayerLogic.player_parameters import Player

PLAYER_MOVEMENT_SPEED = 3
TILE_SCALING = 0.39
TILE_SIZE = 128

ENEMY_GRAVITY = 10


class Map:
    def __init__(self):
        self.player = None
        self.enemy = None
        self.tile_map = None
        self.tile_scaled = None
        self.scene = None
        self.map_matrix = None
        self.last_press_time = None
        self.finish_line_x = None

    def setup(self, map_name):
        # Pour éditer la map, utiliser Tiled (https://www.mapeditor.org/)
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(
            map_name, TILE_SCALING, layer_options)

        platforms_layer = self.tile_map.sprite_lists["Platforms"]
        coins_layer = self.tile_map.sprite_lists["Coins"]
        finish_layer = self.tile_map.sprite_lists["Finish"]

        self.map_matrix = [
            [0 for _ in range(self.tile_map.width)] for _ in range(self.tile_map.height)
        ]

        self.tile_scaled = self.tile_map.tile_width * self.tile_map.scaling

        for sprite in platforms_layer:
            column = int((sprite.center_x) // self.tile_scaled)
            row = int(
                (self.tile_map.height * self.tile_scaled -
                 (sprite.center_y)) // self.tile_scaled
            )

            self.map_matrix[row][column] = 1

        # player_current_y = int(
        #     (self.tile_map.height * TILE_SIZE - self.player.center_y) // TILE_SIZE
        # )

        for sprite in coins_layer:
            column = int((sprite.center_x * TILE_SCALING) // TILE_SIZE)
            row = int(
                (self.tile_map.height * self.tile_map.height - sprite.center_y)
                // TILE_SIZE
            )

            self.map_matrix[row][column] = 2

        for sprite in finish_layer:
            column = int(sprite.center_x // (TILE_SCALING * TILE_SIZE))
            self.finish_line_x = column

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
            self.player.change_y = 0
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

    def is_player_at_finish_line(self):
        if int(self.player.center_x // (self.tile_scaled)) == self.finish_line_x:
            return True

    def get_environment(self):
        map_height = self.tile_map.height
        player_current_x = int(self.player.center_x //
                               (self.tile_scaled))
        # Le y=0 de la matrice est en haut,alors que celui de l'écran
        # est en bas, il faut donc bidouiller un peu
        player_current_y = int(
            (self.tile_map.height * self.tile_scaled -
             self.player.center_y) // self.tile_scaled
        )

        radar_opposite_side = False
        radar_current_side = False
        radar_front = False

        current_gravity = self.player.current_gravity

        try:
            for i in range(player_current_y - 1, -1, -1):
                if current_gravity > 0:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_opposite_side = True
                        break
                else:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_current_side = True
                        break

            for i in range(player_current_x, player_current_x + 2):
                if self.map_matrix[player_current_y][i] == 1:
                    radar_front = True
                    break

            for i in range(player_current_y + 1, map_height, 1):
                if current_gravity > 0:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_current_side = True
                        break
                else:
                    if self.map_matrix[i][player_current_x + 1] == 1:
                        radar_opposite_side = True
                        break
            # if radar_opposite_side is True and radar_front is True and radar_current_side is True:
            #     print("zaejhk")
        except Exception:
            # out of bound
            return (0, 0, 0)
        return (radar_opposite_side, radar_front, radar_current_side)
