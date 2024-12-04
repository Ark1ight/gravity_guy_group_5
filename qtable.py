from random import choice
import pickle

ACTION_CHANGE_GRAV = True
ACTION_DO_NOTHING = False

MOVES = {ACTION_CHANGE_GRAV, ACTION_DO_NOTHING}
ACTIONS = [ACTION_CHANGE_GRAV, ACTION_DO_NOTHING]


def arg_max(table):
    return max(table, key=table.get)


class QTable:
    def __init__(self, learning_rate=1, discount_factor=0.9):
        self.dic = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def get_state_key(self, environment_matrix, player_position, gravity):
        return tuple(map(tuple, environment_matrix)), player_position, gravity

    def set(self, state, action, reward, new_state):
        if state not in self.dic:
            self.dic[state] = {
                ACTION_CHANGE_GRAV: 0,
                ACTION_DO_NOTHING: 0,
            }
        if new_state not in self.dic:
            self.dic[new_state] = {
                ACTION_CHANGE_GRAV: 0,
                ACTION_DO_NOTHING: 0,
            }

        self.dic[state][action] += reward

        delta = (
            reward
            + self.discount_factor * max(self.dic[new_state].values())
            - self.dic[state][action]
        )
        self.dic[state][action] += self.learning_rate * delta
        # Q(s, a) = Q(s, a) + alpha * [reward + gamma * max(S', a) - Q(s, a)]

    def best_action(self, position):
        if position in self.dic:
            return arg_max(self.dic[position])
        else:
            return choice(ACTIONS)

    def save(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.dic, file)

    def load(self, filename):
        with open(filename, "rb") as file:
            self.dic = pickle.load(file)

    def __repr__(self):
        res = " " * 11
        for action in ACTIONS:
            res += f"{action:5s}"
        res += "\r\n"
        for state in self.dic:
            res += str(state) + " "
            for action in self.dic[state]:
                res += f"{self.dic[state][action]:5d}"
            res += "\r\n"
        return res
