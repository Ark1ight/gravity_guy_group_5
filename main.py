"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Gravity Guy"

CHARACTER_SCALING = 0.4
PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
TILE_SCALING = 0.1


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background = None
        self.scene = None

        self.player_sprite = None
        # Our physics engine
        self.physics_engine = None
        self.current_gravity = GRAVITY




    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.background = arcade.load_texture("images/background.png")
        # Initialize Scene
        self.scene = arcade.Scene()

        # Create the Sprite lists
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)


        # Set up the player, specifically placing it at these coordinates.
        image_source = "images/test.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
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

            # Create the 'physics engine'
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite, gravity_constant=self.current_gravity, walls=self.scene["Walls"]
            )


    def on_draw(self):
        """Render the screen."""
        # Code to draw the screen goes here
        self.clear()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        #Draw the scene
        self.scene.draw()

    def on_key_press(self, key, modifiers, current_gravity = GRAVITY):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.Z:
            self.current_gravity *= -1  # Toggling the gravity
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_sprite, gravity_constant=self.current_gravity, walls=self.scene["Walls"]
            )
        elif key == arcade.key.LEFT or key == arcade.key.Q:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.LEFT or key == arcade.key.Q:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()



def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()