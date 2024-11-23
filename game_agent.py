from qtable import QTable


REWARD_DEFAULT = 10
REWARD_COIN = 100
REWARD_GOAL = 1000
REWARD_CHANGE_GRAV = -10
REWARD_DIE = -1000

ACTION_CHANGE_GRAV = True
ACTION_DO_NOTHING = False

MOVES = {ACTION_CHANGE_GRAV, ACTION_DO_NOTHING}
ACTIONS = [ACTION_CHANGE_GRAV, ACTION_DO_NOTHING]


class Agent:
    def __init__(self, env):
        self.env = env
        self.reset()
        self.qtable = QTable()

    def reset(self):
        self.score = 0

    def do(self, action=None):
        if not action:
            action = self.best_action()

        new_position, reward = self.env.move(self.position, action)
        self.qtable.set(self.position, action, reward, new_position)
        self.position = new_position
        self.score += reward

        return action, reward

    def best_action(self):
        return self.qtable.best_action(self.position)

    def __repr__(self):
        return f"{self.position} score:{self.score}"
