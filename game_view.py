# game_view.py
import time
import arcade
from PlayerLogic.player_parameters import Player

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Gravity Guy"
PLAYER_MOVEMENT_SPEED = 3
GRAVITY = 1
TILE_SCALING = 1
DEATH_SCALING = 0.5
def death_screen_display(last_x, last_y):
    img = arcade.load_texture('images/death_skull.png')
    arcade.draw_texture_rectangle(last_x, last_y, 1250 * DEATH_SCALING, 700 * DEATH_SCALING, img)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tile_map = None
        self.scene = None
        self.player = None
        self.physics_engine = None
        self.current_gravity = GRAVITY
        self.camera = None
        self.last_press_time = 0
        self.score = 0
        self.lastPos = 0
        self.is_game_started = 0
        self.map_matrix= None

    def on_show(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)  # Set background color

    def setup(self):
        #Pour éditer la map, utiliser Tiled (https://www.mapeditor.org/)
        map_name = "resources/maps/map.json"

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }

        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        a = self.tile_map.sprite_lists["Platforms"]

        self.map_matrix = [[0 for _ in range(self.tile_map.width)] for _ in range(self.tile_map.height)]

        for sprite in a:
            column = int(sprite.center_x // 128)
            row = int((self.tile_map.height * self.tile_map.height - sprite.center_y) // 128)

            self.map_matrix[row][column] = 1

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.score = 0

        # self.scene = arcade.Scene()
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Creation of Player and Walls list in the base level
        self.scene.add_sprite_list("Player")
        self.player = Player()
        self.scene.add_sprite("Player", self.player)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=self.current_gravity, walls=self.scene["Platforms"]
        )

    def on_draw(self):
        self.clear()
        self.scene.draw()
        if self.player.is_dead:
            death_screen_display(self.player.center_x, self.player.center_y)
        self.camera.use()

    def center_camera_to_player(self):
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def on_key_press(self, key, modifiers, current_gravity=GRAVITY):
        if key == arcade.key.SPACE:
            # Cooldown on gravity skill
            current_time = time.time()
            if current_time - self.last_press_time < self.player.skill_cooldown:
                return
            self.last_press_time = current_time
            # Change of gravity
            self.current_gravity *= -1
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player, gravity_constant=self.current_gravity, walls=self.scene["Platforms"]
            )
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.is_game_started = 1
            self.player.change_x = PLAYER_MOVEMENT_SPEED

    def get_environment(self, current_tile):
        env = None
        for i in range(0, 7):
            for j in range(current_tile, current_tile + 3):
                pass
            #get agent environment (ie, the next three tiles)

    def on_update(self, delta_time):
        if not self.player.is_dead:
            self.physics_engine.update()
            self.center_camera_to_player()
            self.player.is_player_dead(SCREEN_HEIGHT)
            if self.is_game_started:
                if int(self.lastPos) >= int(self.player.center_x % 128):
                    current_tile = (self.player.center_x // 128) + 1
                self.lastPos = self.player.center_x % 128