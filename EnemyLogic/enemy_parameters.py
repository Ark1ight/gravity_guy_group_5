import arcade

CHARACTER_SCALING = 0.2

ENEMY_GRAVITY = 10


class Enemy(arcade.Sprite):
    def __init__(self, image_source="images/test.png"):
        super().__init__(image_source, CHARACTER_SCALING)
        self.is_touching_player = False
        self.time_to_spawn = 0
        self.has_spawned = False

        self.center_x = None
        self.center_y = None

        self.physics_engine = None
        self.current_gravity = ENEMY_GRAVITY

    def spawn(self, x_position):
        # print("Spawning enemy")
        self.center_x = x_position
        self.has_spawned = True

    def set_physics(self, physics):
        self.physics_engine = physics
