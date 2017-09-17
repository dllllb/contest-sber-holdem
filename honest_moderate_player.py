import sys
import json

from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 350

class HonestModeratePlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state, bot_state=None):
        self.update_round_info(round_state)
        my_uuid = self.uuid
        if bot_state is not None:
            my_current_stack = bot_state['stack']
            time_to_action = bot_state['time_limit_action']
            time_bank_remaining = bot_state['time_limit_bank']
            total_time_remaining = time_bank_remaining + time_to_action

        if self.nb_player < 2:
            action = valid_actions[1]  # fetch CALL action info
        else:
            community_card = round_state['community_card']
            win_rate = estimate_hole_card_win_rate(
                    nb_simulation=NB_SIMULATION,
                    nb_player=self.nb_player,
                    hole_card=gen_cards(hole_card),
                    community_card=gen_cards(community_card)
                    )
            if win_rate >= 0.7:
                try:
                    action = valid_actions[2]  # fetch RAISE action info
                    action['amount'] = action['amount']['max']
                except:
                    # all-in already
                    action = valid_actions[1]  # fetch CALL action info
            elif win_rate >= 0.5:
                try:
                    action = valid_actions[2]  # fetch RAISE action info
                    action['amount'] = action['amount']['min']
                except:
                    # all-in already
                    action = valid_actions[1]  # fetch CALL action info
            elif win_rate >= 1.0 / self.nb_player:
                action = valid_actions[1]  # fetch CALL action info
            else:
                action = valid_actions[0]  # fetch FOLD action info

        return action['action'], action['amount']


    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hole_card = hole_card
        self.seats = seats
        self.round_count = round_count

    def receive_street_start_message(self, street, round_state):
        self.update_round_info(round_state)
        self.street = street

    def update_round_info(self, round_state):
        self.actions_hist  = round_state['action_histories']
        self.community_card = round_state['community_card']
        self.seats = round_state['seats']
        self.round_state = round_state
        self.nb_player = len([pl for pl in self.seats if pl['state'] == 'participating'])

    def receive_game_update_message(self, action, round_state):
        self.update_round_info(round_state)

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
