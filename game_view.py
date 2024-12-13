# game_view.py
import time
import arcade
import arcade.color

from EnemyLogic.enemy_parameters import Enemy
from PlayerLogic.player_parameters import Player
from qtable import QTable

REWARD_DEFAULT = 10
REWARD_COIN = 100
REWARD_GOAL = 1000
REWARD_CHANGE_GRAV = -15
REWARD_DIE = -1000

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Gravity Guy"
PLAYER_MOVEMENT_SPEED = 3

PLAYER_GRAVITY = 10
ENEMY_GRAVITY = 10
TILE_SCALING = 1
DEATH_SCALING = 0.5
ENEMY_SPAWN_DELAY = 1

def death_screen_display(last_x, last_y):
    img = arcade.load_texture("images/death_skull.png")
    arcade.draw_texture_rectangle(
        last_x, last_y, 1250 * DEATH_SCALING, 700 * DEATH_SCALING, img
    )


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tile_map = None
        self.scene = None
        self.player = None

        self.enemy_bot = None
        self.enemy_bot_spawn_time = 0
        self.has_enemy_spawned = False

        self.physics_engine = None
        self.enemy_physics_engine = None

        self.player_current_gravity = PLAYER_GRAVITY
        self.enemy_current_gravity = ENEMY_GRAVITY

        self.camera = None
        self.last_press_time = 0
        self.score = 0
        self.lastPos = 0
        self.is_game_started = 0
        self.map_matrix = None
        self.qtable = QTable()

        self.action_history = []
        self.score_history = []
        self.state_history = []



    def on_show(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)  # Set background color

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

        self.scene.add_sprite_list("Enemy")
        self.enemy_bot = None

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=self.player_current_gravity,
            walls=self.scene["Platforms"],
        )

        # self.qtable = QTable()

    def spawn_enemy(self):
        if self.enemy_bot is None:  # Spawn only if no enemy exists
            print("Spawning enemy")
            self.enemy_bot = Enemy()
            self.enemy_bot.center_x = 200  # Adjust position as needed
            self.enemy_bot.center_y = 300  # Adjust position as needed

            self.enemy_physics_engine = arcade.PhysicsEnginePlatformer(
                self.enemy_bot,
                gravity_constant=self.enemy_current_gravity,
                walls=self.scene["Platforms"],
            )
            self.scene.add_sprite("Enemy", self.enemy_bot)
            self.has_enemy_spawned = True


    def on_draw(self):
        self.clear()
        self.scene.draw()
        if self.player.is_dead:
            death_screen_display(self.player.center_x, self.player.center_y)
        self.camera.use()
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = 0
        arcade.draw_text(
            self.score, screen_center_x, screen_center_y, arcade.color.BLACK, 20
        )

    def center_camera_to_player(self):
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = 0
        # if screen_center_x < 0:
        #     screen_center_x = 0
        # if screen_center_y < 0:
        #     screen_center_y = 0
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def change_gravity(self, do_change_grav):
        if not do_change_grav:
            return
        # Cooldown on gravity skill
        current_time = time.time()
        if current_time - self.last_press_time < self.player.skill_cooldown:
            return
        self.last_press_time = current_time
        # Change of gravity
        self.player_current_gravity *= -1
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=self.player_current_gravity,
            walls=self.scene["Platforms"],
        )
        self.score += REWARD_CHANGE_GRAV

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.change_gravity(True)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.is_game_started = 1
            self.player.change_x = PLAYER_MOVEMENT_SPEED

    def get_environment(self, current_tile):
        env = []
        for i in range(0, 7):
            env.append([])
            for j in range(current_tile, current_tile + 3):
                env[i].append(self.map_matrix[i][j])

        player_x_pos = int(self.player.center_y // 128)
        # A voir sous quel format envoyer l'environnement a la qtable
        return env, player_x_pos, self.player_current_gravity

    def get_score(self):
        if self.player.is_player_dead(SCREEN_HEIGHT):
            self.score += REWARD_DIE
        else:
            self.score += REWARD_DEFAULT

    def restart_game(self):
        # Player restart
        self.player.center_x = 200
        self.player.center_y = 300
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.is_dead = False
        self.player.change_x = PLAYER_MOVEMENT_SPEED

        # Enemy restart
        if self.enemy_bot:
            self.enemy_bot.remove_from_sprite_lists()
            self.enemy_bot = None
        self.enemy_bot_spawn_time = 0
        self.has_enemy_spawned = False

        # Game restart
        self.is_game_started = 1
        self.player_current_gravity = PLAYER_GRAVITY
        self.action_history = []
        self.score_history = []
        self.state_history = []
        self.score = 0
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=self.player_current_gravity,
            walls=self.scene["Platforms"],
        )

    def on_update(self, delta_time):
        if not self.player.is_dead:
            self.physics_engine.update()
            self.center_camera_to_player()
            self.player.is_player_dead(SCREEN_HEIGHT)
            if self.player.is_dead:
                self.score += REWARD_DIE
                current_tile = int(self.player.center_x // 128)
                env, player_pos, gravity = self.get_environment(current_tile)
                state = self.qtable.get_state_key(env, player_pos, gravity)
                self.qtable.set(
                    self.state_history[-1],
                    self.action_history[-1],
                    self.score - self.score_history[-1],
                    self.state_history[-1],
                )
                self.restart_game()

            if self.is_game_started:
                if int(self.lastPos) >= int(self.player.center_x % 128):
                    current_tile = int(self.player.center_x // 128)
                    self.get_score()
                    env, player_pos, gravity = self.get_environment(current_tile)
                    state = self.qtable.get_state_key(env, player_pos, gravity)
                    action = self.qtable.best_action(state)
                    self.change_gravity(action)
                    self.qtable.set(
                        state,
                        action,
                        self.score
                        - (self.score_history[-1] if self.score_history else 0),
                        self.state_history[-1] if self.state_history else None,
                    )
                    self.action_history.append(action)
                    self.state_history.append(state)
                    self.score_history.append(self.score)
                self.lastPos = self.player.center_x % 128

        if not self.has_enemy_spawned and self.is_game_started:
            self.enemy_bot_spawn_time += delta_time
            if self.enemy_bot_spawn_time >= ENEMY_SPAWN_DELAY:
                self.spawn_enemy()
                self.enemy_bot_spawn_time = 0  # Reset the spawn timer

        if self.enemy_bot and self.enemy_physics_engine:
            self.enemy_physics_engine.update()
            # Update the enemy's position and check if it goes off-screen
        if self.enemy_bot:
            self.enemy_bot.update()
            self.enemy_bot.center_x += 3  # Move enemy to the left
            if self.enemy_bot.center_x < 0:  # Enemy goes off-screen
                self.enemy_bot.remove_from_sprite_lists()
                self.enemy_bot = None
                self.enemy_spawned = False  # Allow the enemy to respawn

