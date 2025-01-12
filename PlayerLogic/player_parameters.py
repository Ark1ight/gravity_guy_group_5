# player_parameters.py
import arcade

PLAYER_GRAVITY = 5

CHARACTER_SCALING = 0.1
STARTING_X = 200
STARTING_Y = 300
TILE_SCALING = 0.39


class Player(arcade.Sprite):
    def __init__(self, image_source="images/test.png"):
        super().__init__(image_source, CHARACTER_SCALING)

        self.center_x = STARTING_X
        self.center_y = STARTING_Y
        self.change_x = 0
        self.change_y = 0

        self.physics_engine = None
        self.current_gravity = PLAYER_GRAVITY

        self.skill_cooldown = 0.5
        self.is_dead = False

        self.radar_opposite_side = None
        self.radar_front = None
        self.radar_current_side = None

        self.score_change = None
        self.score_keep = None

    def player_respawn(self):
        self.center_x = STARTING_X
        self.center_y = STARTING_Y
        self.current_gravity = PLAYER_GRAVITY

    def relative_center_x(self):
        return self.center_x * TILE_SCALING

    def relative_center_y(self):
        return self.center_y * TILE_SCALING

    def is_player_dead(self, screen_height):
        if self.relative_center_y() < 0 or self.relative_center_y() > screen_height + 100:
            self.is_dead = True
