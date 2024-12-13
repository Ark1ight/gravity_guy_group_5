import arcade

CHARACTER_SCALING = 0.2

class Enemy(arcade.Sprite):
    def __init__(self, image_source="images/shrek2.jpg"):
        super().__init__(image_source, CHARACTER_SCALING)
        self.is_touching_player = False
        self.time_to_spawn = 0