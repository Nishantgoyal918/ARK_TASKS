# !/usr/bin/env python
import sys
import operator
import click

from gym_tictactoe.env import TicTacToeEnv, agent_by_mark, check_game_status, \
    after_action_state, tomark, next_mark, tocode


class HumanAgent(object):
    def __init__(self, mark):
        self.mark = mark

    def act(self, state, ava_actions):
        while True:
            uloc = input("Enter location[1-9], q for quit: ")
            if uloc.lower() == 'q':
                return None
            try:
                action = int(uloc) - 1
                if action not in ava_actions:
                    raise ValueError()
            except ValueError:
                print("Illegal location: '{}'".format(uloc))
            else:
                break

        return action

#It finds the optimal move using minimax algo
def find_loc_prob(state, aval_actions, action, win_count, loss_count, step):
    aval_actions.remove(action)
    state = after_action_state(state, action)
    game_status = check_game_status(state[0])

    if (game_status == 0 or game_status == tocode(next_mark(state[1]))):
        win_count = win_count + step

        if (game_status == 0):	#If there is draw then it will be counted as victory for both the players
            loss_count = loss_count + step

        return win_count, loss_count
    elif (game_status == tocode(state[1])):
        loss_count = loss_count + step
        return win_count, loss_count
    else:
        for action in aval_actions:
            temp = aval_actions.copy()
            loss_count, win_count = find_loc_prob(state, temp, action, loss_count, win_count, step/5)

    return win_count, loss_count


class MinimaxAgent(object):

    def __init__(self, mark):
        self.mark = mark

    def act(self, state, ava_actions):
        location_probability = []
        #print(ava_actions)
        for items in ava_actions:
            temp = ava_actions.copy() #Creating a copy of ava_actions inorder to prevent call by reference.
            (win_count, loss_count) = find_loc_prob(state, temp, items, 0.0, 0.0, 1000)
            location_probability.append(win_count - loss_count)

        #print(location_probability)

        max_value = location_probability[0]
        max_value_index = 0
        for values in location_probability:
            if (values > max_value):
                max_value_index = location_probability.index(values)
                max_value = values
                #print(max_value_index)

        return ava_actions[max_value_index]


#   return the move in this function. ava_actions is an array containting the possible actions
#   you might want to use after_action_state and check_game_status. Also look at env.py
#   state is a tuple with the first value indicating the board and second value indicating mark
#   proper use of inbuilt functions will avoid interacting with state

@click.command(help="Play minimax agent.")
@click.option('-n', '--show-number', is_flag=True, default=False,
              show_default=True, help="Show location number in the board.")
def play(show_number):
    env = TicTacToeEnv(show_number=show_number)
    agents = [MinimaxAgent('O'),
              HumanAgent('X')]
    episode = 0
    while True:
        state = env.reset()
        _, mark = state
        done = False
        env.render()
        while not done:
            agent = agent_by_mark(agents, mark)
            env.show_turn(True, mark)
            ava_actions = env.available_actions()
            action = agent.act(state, ava_actions)
            if action is None:
                sys.exit()

            state, reward, done, info = env.step(action)

            print('')
            env.render()
            if done:
                env.show_result(True, mark, reward)
                break
            else:
                _, _ = state
            mark = next_mark(mark)

        episode += 1


if __name__ == '__main__':
    play()
