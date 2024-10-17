# game_view.py
import time
import arcade
from PlayerLogic.player_parameters import Player

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Gravity Guy"
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
TILE_SCALING = 0.1
DEATH_SCALING = 0.5
def death_screen_display(last_x, last_y):
    img = arcade.load_texture('images/death_skull.png')
    arcade.draw_texture_rectangle(last_x, last_y, 1250 * DEATH_SCALING, 700 * DEATH_SCALING, img)

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.scene = None
        self.player = None
        self.physics_engine = None
        self.current_gravity = GRAVITY
        self.camera = None
        self.last_press_time = 0

        self.background = arcade.load_texture("images/background.png")
        self.background_x = 0  # initial x pos
        self.background_y = 0  # initial y pos

    def setup(self):
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        #creation of Player and Walls list in the base level
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.player = Player()
        self.scene.add_sprite("Player", self.player)

        for x in range(0, 1250, 64):
            wall = arcade.Sprite("images/shrek2.jpg", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        for x in range(0, 320, 64):
            wall = arcade.Sprite("images/shrek2.jpg", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 500
            self.scene.add_sprite("Walls", wall)

        for x in range(325, 700, 64):
            wall = arcade.Sprite("images/shrek2.jpg", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 200
            self.scene.add_sprite("Walls", wall)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=self.current_gravity, walls=self.scene["Walls"]
        )

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        self.scene.draw()
        if self.player.is_dead:
            death_screen_display(self.player.center_x,self.player.center_y)
        self.camera.use()

    def center_camera_to_player(self):
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def on_key_press(self, key, modifiers, current_gravity=GRAVITY):
        if key == arcade.key.SPACE:

            #cooldown on gravity skill
            current_time = time.time()
            if current_time - self.last_press_time < self.player.skill_cooldown:
                return
            self.last_press_time = current_time
            #change of gravity
            self.current_gravity *= -1
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player, gravity_constant=self.current_gravity, walls=self.scene["Walls"]
            )
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED

    def on_update(self, delta_time):
        if not self.player.is_dead:
            self.physics_engine.update()
            self.center_camera_to_player()
            self.player.is_player_dead(SCREEN_HEIGHT)
