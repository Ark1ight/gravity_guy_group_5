import arcade


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width=width, height=height, title=title)
        self.set_update_rate(1 / 120)
