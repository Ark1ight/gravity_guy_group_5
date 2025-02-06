import arcade

import game_view
from game_window import GameWindow
from menu_view import MenuView

# Constantes pour la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Menu Principal Arcade"


def main():
    """Fonction principale"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    qtable_filename = "qtable_save.pk"
    menu_view = MenuView(qtable_filename)
    window.show_view(menu_view)
    arcade.run()
    menu_view.game_view.qtable.save(qtable_filename)
    menu_view.game_view.show_graph()


if __name__ == "__main__":
    main()
