from pypokerengine.players import BasePokerPlayer
from bot_features import vectorize_state, win_rate_calc_py, win_rate_calc_cpp


class TemplatePlayer(BasePokerPlayer):
    def __init__(self, props):
        super().__init__()

        wr_calc = props.get('wr_calc', 'py')
        if wr_calc == 'py':
            self.wrc = win_rate_calc_py
        else:
            self.wrc = win_rate_calc_cpp

    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        features = vectorize_state(self.uuid, round_state, bot_state, valid_actions, hole_card, self.wrc)
        return self.strategy(features, valid_actions)

    def strategy(self, features, valid_actions):
        pass

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def update_round_info(self, round_state):
        pass
