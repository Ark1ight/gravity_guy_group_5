import arcade
import arcade.color
import matplotlib.pyplot as plt

from game_map import Map
from qtable import QTable

REWARD_DEFAULT = 0
REWARD_COIN = 100
REWARD_GOAL = 1000
REWARD_CHANGE_GRAV = -5
REWARD_DIE = -1000
REWARD_WALL = -50

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Gravity Guy"
PLAYER_MOVEMENT_SPEED = 3

PLAYER_GRAVITY = 10
ENEMY_GRAVITY = 10
TILE_SCALING = 0.39
DEATH_SCALING = 0.5
ENEMY_SPAWN_DELAY = 1

TILE_SIZE = 128


# def death_screen_display(last_x, last_y):
#     img = arcade.load_texture("images/death_skull.png")
#     arcade.draw_texture_rectangle(
#         last_x, last_y, 1250 * DEATH_SCALING, 700 * DEATH_SCALING, img
#     )

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.map = None

        self.camera = None
        self.score = 0
        self.last_action_pos = 0
        self.last_it_pos_x = 0
        self.last_it_pos_y = 0
        self.is_game_started = 0
        self.qtable = QTable()

        self.action_history = []
        self.score_history = []
        self.state_history = []
        self.run_result_history = []

    def on_show(self):
        arcade.set_background_color(
            arcade.color.SKY_BLUE)  # Set background color

    def setup(self):
        self.map = Map()
        self.map.setup()
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # def spawn_enemy(self, x_position):
    #     self.map.spawn_enemy(x_position)

    def show_graph(self):
        plt.plot(self.run_result_history)
        plt.title("Score evolution")
        plt.xlabel("Run")
        plt.ylabel("Score")
        plt.show()

    def on_draw(self):
        self.clear()
        try:
            self.map.scene.draw()
            self.camera.use()
            self.draw_hud()
        except Exception:
            pass

    def draw_hud(self):
        screen_center_x = self.map.player.center_x - \
            (self.camera.viewport_width / 2)
        screen_center_y = 0
        arcade.draw_text(
            self.score, screen_center_x, screen_center_y, arcade.color.BLACK, 20
        )
        arcade.draw_text(
            "Opposite:" + str(self.map.player.radar_opposite_side),
            screen_center_x + 50,
            screen_center_y + 100,
            arcade.color.BLACK,
            20,
        )
        arcade.draw_text(
            "Front:" + str(self.map.player.radar_front),
            screen_center_x + 50,
            screen_center_y + 50,
            arcade.color.BLACK,
            20,
        )
        arcade.draw_text(
            "Current:" + str(self.map.player.radar_current_side),
            screen_center_x + 50,
            screen_center_y,
            arcade.color.BLACK,
            20,
        )
        arcade.draw_text(
            "Keep:" + str(self.map.player.score_keep),
            screen_center_x + 250,
            screen_center_y,
            arcade.color.BLACK,
            20,
        )
        arcade.draw_text(
            "Change:" + str(self.map.player.score_change),
            screen_center_x + 250,
            screen_center_y + 50,
            arcade.color.BLACK,
            20,
        )

    def center_camera_to_player(self):
        screen_center_x = self.map.player.center_x - \
            (self.camera.viewport_width / 2)
        screen_center_y = 0
        player_centered = screen_center_x, screen_center_y
        self.camera.move_to(player_centered)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.map.change_player_gravity(True)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.is_game_started = 1
            self.map.player.change_x = PLAYER_MOVEMENT_SPEED

    def get_environment(self):
        env = self.map.get_environment()
        self.map.player.radar_opposite_side = env[0]
        self.map.player.radar_front = env[1]
        self.map.player.radar_current_side = env[2]
        return env

    def get_score(self, do_change_grav=None):
        if self.map.player.is_dead:
            self.score += REWARD_DIE
        elif int(self.last_it_pos_x) == int(self.map.player.center_x):
            self.score += REWARD_WALL
        elif do_change_grav:
            self.score += REWARD_CHANGE_GRAV
        else:
            self.score += REWARD_DEFAULT

    def restart_game(self):
        # Player restart
        # self.__init__()

        # Game restart
        self.run_result_history.append(self.score)
        self.is_game_started = 1
        self.map.setup()
        self.action_history = []
        self.score_history = []
        self.state_history = []
        self.score = 0
        self.last_action_pos = 0
        self.last_it_pos_x = 0
        self.map.player.change_x = PLAYER_MOVEMENT_SPEED

    def get_agent_action(self):
        self.last_action_pos = int(
            self.map.player.center_x // self.map.tile_scaled)

        env = self.get_environment()
        state = self.qtable.get_state_key(env)
        action = self.qtable.best_action(state)
        self.get_score(action)
        self.map.change_player_gravity(action)
        choices = self.qtable.dic[state] if state in self.qtable.dic else None
        self.map.player.score_change = choices[True] if choices else None
        self.map.player.score_keep = choices[False] if choices else None
        self.qtable.set(
            state,
            action,
            self.score - (self.score_history[-1] if self.score_history else 0),
        )
        self.action_history.append(action)
        self.state_history.append(state)
        self.score_history.append(self.score)

    def do_player_choose_action(self):
        if self.last_action_pos < int(self.map.player.center_x // self.map.tile_scaled):
            return True
        elif int(self.last_it_pos_x) == int(self.map.player.center_x) and int(self.last_it_pos_y) == int(self.map.player.center_y):
            return True
        return False

    def finish_line(self):
        if self.map.is_player_at_finish_line():
            self.score += REWARD_GOAL
            self.qtable.set(
                self.state_history[-1],
                self.action_history[-1],
                self.score - self.score_history[-1],
            )
            self.restart_game()

    def on_update(self, delta_time):
        # Player update
        if not self.map.player.is_dead:
            self.map.player.physics_engine.update()
            self.center_camera_to_player()

            self.map.player.is_player_dead(SCREEN_HEIGHT)
            if self.map.player.is_dead:
                self.get_score()
                self.qtable.set(
                    self.state_history[-1],
                    self.action_history[-1],
                    self.score - self.score_history[-1],
                )
                self.restart_game()
            self.finish_line()
            # Game update
            if self.is_game_started:
                if self.do_player_choose_action():
                    self.get_agent_action()
                self.last_it_pos_x = self.map.player.center_x
                self.last_it_pos_y = self.map.player.center_y

                # Ennemy Logic

                #     if self.has_enemy_spawned and len(self.action_history) >= 3:
                #         action = self.action_history[-3]
                #         if action == ACTION_CHANGE_GRAV:
                #             self.enemy_current_gravity *= -1
                #             self.enemy_physics_engine = arcade.PhysicsEnginePlatformer(
                #                 self.map.enemy,
                #                 gravity_constant=self.enemy_current_gravity,
                #                 walls=self.map.scene["Platforms"],
                #             )

                #     if (
                #         not self.has_enemy_spawned
                #         and self.is_game_started
                #         and len(self.action_history) >= 2
                #     ):
                #         self.spawn_enemy(self.map.player.center_x - SPRITE_SIZE * 2)
                # self.lastPos = self.map.player.center_x % SPRITE_SIZE
        # Enemy update

        # if self.has_enemy_spawned and self.map.enemy and self.enemy_physics_engine:
        #     self.enemy_physics_engine.update()
        #     self.map.enemy.update()
        #     self.map.enemy.center_x += PLAYER_MOVEMENT_SPEED

        #     if self.map.player.is_dead:
        #         self.map.enemy.remove_from_sprite_lists()
        #         self.map.enemy = None
        #         # Allow the enemy to respawn
