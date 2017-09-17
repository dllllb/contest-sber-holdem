import sys
import json
import pandas as pd
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

NB_SIMULATION = 300

class AntiFoldPlayer(BasePokerPlayer):
    def __init__(self, streets_count_average_file='streets_count_average_2017-09-16.csv'):
        try:
            self.streets_count_average = pd.read_csv(streets_count_average_file).set_index('name')['streets_count_average']
            self.foldbots = set(self.streets_count_average[self.streets_count_average==1].index)
        except:
            # print('Error loading', streets_count_average_file )
            self.streets_count_average = pd.Series([])
            self.foldbots = set({})
    
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
            win_rate = 1.
        else:
            community_card = round_state['community_card']
            win_rate = estimate_hole_card_win_rate(
                    nb_simulation=NB_SIMULATION,
                    nb_player=self.nb_player,
                    hole_card=gen_cards(hole_card),
                    community_card=gen_cards(community_card)
                    )
            if win_rate >= 0.9:
                try:
                    action = valid_actions[2]  # fetch RAISE action info
                    action['amount'] = action['amount']['max']
                except:
                    # all-in already
                    action = valid_actions[1]  # fetch CALL action info
            elif win_rate >= 0.7:
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

        # print('win_rate', win_rate, 'action', action)
        return action['action'], action['amount']


    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hole_card = hole_card
        self.seats = seats
        self.round_count = round_count

    def receive_street_start_message(self, street, round_state):
        self.street = street # important to update before round_state
        self.update_round_info(round_state)

    def update_round_info(self, round_state):
        self.actions_hist  = round_state['action_histories']
        self.community_card = round_state['community_card']
        self.seats = round_state['seats']
        self.round_state = round_state
        if self.street == 'preflop':
            self.nb_player = len([pl for pl in self.seats 
                                  if (pl['state'] == 'participating')
                                  and (pl['name'] not in self.foldbots)])
        else:
            self.nb_player = len([pl for pl in self.seats if pl['state'] == 'participating'])
            # if foldman bot is participating, exclude him 
            participating = set([pl['name'] for pl in self.seats if pl['state'] == 'participating'])
            participating_foldbots = self.foldbots & participating
            if len(participating_foldbots) > 0:
                # print('Not a foldbot:', participating_foldbots)
                self.foldbots = self.foldbots - participating

    def receive_game_update_message(self, action, round_state):
        self.update_round_info(round_state)

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
