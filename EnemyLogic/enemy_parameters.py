import arcade

CHARACTER_SCALING = 0.2

class Enemy(arcade.Sprite):
    def __init__(self, image_source="images/test.png"):
        super().__init__(image_source, CHARACTER_SCALING)
        self.is_touching_player = False
        self.time_to_spawn = 0

    def spawn(self, gameview, x_position):
        if gameview.enemy_bot is None:
            print("Spawning enemy")
            gameview.enemy_bot = Enemy()
            gameview.enemy_bot.center_x = x_position
            gameview.enemy_bot.center_y = 300

            gameview.enemy_physics_engine = arcade.PhysicsEnginePlatformer(
                gameview.enemy_bot,
                gravity_constant=gameview.enemy_current_gravity,
                walls=gameview.scene["Platforms"],
            )
            gameview.scene.add_sprite("Enemy", gameview.enemy_bot)
            gameview.has_enemy_spawned = True