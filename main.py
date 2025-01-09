import arcade

import game_view
from game_view import GameView
from game_window import GameWindow

# Constantes pour la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Menu Principal Arcade"


class MenuView(arcade.View):
    game_view = None
    def __init__(self):
        super().__init__()
    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            arcade.load_texture("images/background.png"),
        )
        # Titre
        arcade.draw_text(
            "Gravity Guy",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            font_size=50,
            anchor_x="center",
        )
        # Option "Jouer"
        arcade.draw_text(
            "Appuyez sur Entrée pour jouer",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.YELLOW,
            font_size=30,
            anchor_x="center",
        )
        # Option "Quitter"
        arcade.draw_text(
            "Appuyez sur 'Esc' pour quitter",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 50,
            arcade.color.RED,
            font_size=30,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            # lauching game view
            self.game_view = GameView()
            # Initialise view
            self.game_view.setup()
            self.window.show_view(self.game_view)
        elif key == arcade.key.ESCAPE:
            arcade.close_window()


def main():
    """Fonction principale"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()
    menu_view.game_view.show_graph()

if __name__ == "__main__":
    main()
