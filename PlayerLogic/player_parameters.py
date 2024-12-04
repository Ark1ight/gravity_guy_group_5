# player_parameters.py
import arcade

CHARACTER_SCALING = 0.2


class Player(arcade.Sprite):
    def __init__(self, image_source="images/test.png"):
        super().__init__(image_source, CHARACTER_SCALING)

        self.center_x = 200
        self.center_y = 300
        self.change_x = 0
        self.change_y = 0

        self.skill_cooldown = 0.5
        self.is_dead = False

    def is_player_dead(self, screen_height):
        if self.center_y < 0 or self.center_y > screen_height + 100:
            self.is_dead = True
