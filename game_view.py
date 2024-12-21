import time
import arcade
import arcade.color

from EnemyLogic.enemy_parameters import Enemy
from PlayerLogic.player_parameters import Player
from game_agent import ACTION_CHANGE_GRAV
from game_map import Map
from qtable import QTable

REWARD_DEFAULT = 10
REWARD_COIN = 100
REWARD_GOAL = 1000
REWARD_CHANGE_GRAV = -15
REWARD_DIE = -1000
REWARD_WALL = -50

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
        #MAP
        self.map = None

        self.has_enemy_spawned = False

        #ENGINE
        self.physics_engine = None
        self.enemy_physics_engine = None

        #GRAVITY
        # self.map.player_current_gravity = PLAYER_GRAVITY
        # self.enemy_current_gravity = ENEMY_GRAVITY

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
        self.map = Map()
        self.map.setup()
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)


        # self.qtable = QTable()

    def spawn_enemy(self, x_position):
        # Enemy.spawn(self.map.enemy_bot, self, x_position)
        pass


    def on_draw(self):
        self.clear()
        self.map.scene.draw()
        if self.map.player.is_dead:
            death_screen_display(self.map.player.center_x, self.map.player.center_y)
        self.camera.use()
        screen_center_x = self.map.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = 0
        arcade.draw_text(
            self.score, screen_center_x, screen_center_y, arcade.color.BLACK, 20
        )

    def center_camera_to_player(self):
        screen_center_x = self.map.player.center_x - (self.camera.viewport_width / 2)
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
        if current_time - self.last_press_time < self.map.player.skill_cooldown:
            return
        self.last_press_time = current_time
        # Change of gravity
        self.map.player_current_gravity *= -1
        self.map.physics_engine = arcade.PhysicsEnginePlatformer(
            self.map.player,
            gravity_constant=self.map.player_current_gravity,
            walls=self.map.scene["Platforms"],
        )
        self.score += REWARD_CHANGE_GRAV

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.change_gravity(True)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.is_game_started = 1
            self.map.player.change_x = PLAYER_MOVEMENT_SPEED

    def get_environment(self, current_tile):
        return self.map.get_environment(current_tile)

    def get_score(self):
        if self.map.player.is_player_dead(SCREEN_HEIGHT):
            self.score += REWARD_DIE
        else:
            self.score += REWARD_DEFAULT

    def restart_game(self):
        # Player restart
        self.map.player.center_x = 200
        self.map.player.center_y = 300
        self.map.player.change_x = 0
        self.map.player.change_y = 0
        self.map.player.is_dead = False
        self.map.player.change_x = PLAYER_MOVEMENT_SPEED

        # Enemy restart
        if self.map.enemy_bot:
            self.map.enemy_bot.remove_from_sprite_lists()
            self.map.enemy_bot = None
        self.has_enemy_spawned = False

        # Game restart
        self.is_game_started = 1
        self.map.player_current_gravity = PLAYER_GRAVITY
        self.action_history = []
        self.score_history = []
        self.state_history = []
        self.score = 0
        self.map.physics_engine = arcade.PhysicsEnginePlatformer(
            self.map.player,
            gravity_constant=self.map.player_current_gravity,
            walls=self.map.scene["Platforms"],
        )

    def on_update(self, delta_time):

        # Player update
        if not self.map.player.is_dead:
            self.map.physics_engine.update()
            self.center_camera_to_player()
            self.map.player.is_player_dead(SCREEN_HEIGHT)
            if self.map.player.is_dead:
                self.score += REWARD_DIE
                current_tile = int(self.map.player.center_x // 128)
                env, player_pos, gravity = self.get_environment(current_tile)
                state = self.qtable.get_state_key(env, player_pos, gravity)
                self.qtable.set(
                    self.state_history[-1],
                    self.action_history[-1],
                    self.score - self.score_history[-1]
                )
                self.restart_game()
        #Game update
            if self.is_game_started:
                if int(self.lastPos) >= int(self.map.player.center_x % 128):
                    #Player Logic
                    current_tile = int(self.map.player.center_x // 128)
                    self.get_score()
                    env, player_pos, gravity = self.get_environment(current_tile)
                    state = self.qtable.get_state_key(env, player_pos, gravity)
                    action = self.qtable.best_action(state)
                    self.change_gravity(action)
                    self.qtable.set(
                        state,
                        action,
                        self.score
                        - (self.score_history[-1] if self.score_history else 0)
                    )
                    self.action_history.append(action)
                    self.state_history.append(state)
                    self.score_history.append(self.score)

                    #Ennemy Logic

                    if self.has_enemy_spawned and len(self.action_history) >= 3:
                        action = self.action_history[-3]
                        if action == ACTION_CHANGE_GRAV:
                            self.enemy_current_gravity *= -1
                            self.enemy_physics_engine = arcade.PhysicsEnginePlatformer(
                                self.map.enemy_bot,
                                gravity_constant=self.enemy_current_gravity,
                                walls=self.map.scene["Platforms"],
                            )

                    if not self.has_enemy_spawned and self.is_game_started and len(self.action_history) >= 2:
                        self.spawn_enemy(self.map.player.center_x - 128 * 2)
                self.lastPos = self.map.player.center_x % 128
        # Enemy update


        if self.has_enemy_spawned and self.map.enemy_bot and self.enemy_physics_engine:
            self.enemy_physics_engine.update()
            self.map.enemy_bot.update()
            self.map.enemy_bot.center_x += PLAYER_MOVEMENT_SPEED

            if self.map.player.is_dead:
                self.map.enemy_bot.remove_from_sprite_lists()
                self.map.enemy_bot = None
                # Allow the enemy to respawn

