import numpy as np
import pandas as pd
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import calc_winrate


def win_rate_calc_py(round_state, hole_card, n_players):
    if n_players < 2:
        return 1.

    win_rate = estimate_hole_card_win_rate(
        nb_simulation=350,
        nb_player=n_players,
        hole_card=gen_cards(hole_card),
        community_card=gen_cards(round_state['community_card'])
    )
    return win_rate


def street2num(street):
    return ['preflop', 'flop', 'turn', 'river'].index(street)


def win_rate_calc_cpp(round_state, hole_card, n_players):
    holds_per_round = [0, 0, 0, 0]

    for street, actions in round_state['action_histories'].items():
        sn = street2num(street)
        n_folded = sum([1 for a in actions if a['action'] == 'FOLD'])
        holds_per_round[sn] = n_folded

    win_rate = calc_winrate.calc(
        10000,
        [e.encode() for e in hole_card],
        [e.encode() for e in round_state['community_card']],
        holds_per_round,
        n_players - 1)

    return win_rate


def vectorize_state(uuid, round_state, bot_state, valid_actions, hole_card, time_fts=True):
    '''
    declare_action(...)
    state = vectorize_state(uuid, round_state, bot_state, valid_actions, hole_card)
    '''

    features = pd.Series()
    features.loc['main_pot'] = round_state['pot']['main']['amount']
    if 'side' in round_state['pot'] and len(round_state['pot']['side']) > 0:
        side_pot = round_state['pot']['side']
        features.loc['side_pot'] = sum([x['amount'] for x in side_pot])
        # features.loc['side_pot_len'] = len(side_pot['eligibles'])
        # features.loc['side_pot_self'] = uuid in side_pot['eligibles']
    else:
        features.loc['side_pot'] = 0
        # features.loc['side_pot_len'] = 0
        # features.loc['side_pot_self'] = False
    # features.loc['side_pot1']
    features.loc['street'] = street2num(round_state['street'])
    features.loc['round_count'] = round_state['round_count']
    if len(valid_actions) > 1:
        features.loc['call_amount'] = valid_actions[1]['amount']
    else:
        features.loc['call_amount'] = np.nan
    if len(valid_actions) > 2:
        features.loc['raise_amount_min'] = valid_actions[2]['amount']['min']
        features.loc['raise_amount_max'] = valid_actions[2]['amount']['max']
    else:
        features.loc['raise_amount_min'] = np.nan
        features.loc['raise_amount_max'] = np.nan

    n_players = sum([p['state'] in {'participating', 'allin'} for p in round_state['seats']])
    features.loc['n_players'] = n_players

    features.loc['win_rate'] = win_rate_calc_cpp(round_state, hole_card, n_players)

    features.loc['current_stack'] = filter(lambda x: x['uuid'] == uuid, round_state['seats']).__next__()['stack']
    # my_uuid = self.uuid
    if time_fts:
        if bot_state is not None:
            # features.loc['current_stack'] = bot_state['stack']
            features.loc['time_to_action'] = bot_state['time_limit_action']
            features.loc['time_bank_remaining'] = bot_state['time_limit_bank']
            features.loc['total_time_remaining'] = features.loc['time_bank_remaining'] + features.loc['time_to_action']
        else:
            # features.loc['current_stack'] = 1500
            features.loc['time_to_action'] = np.nan
            features.loc['time_bank_remaining'] = np.nan
            features.loc['total_time_remaining'] = np.nan

    comb = ''.join(sorted([c[1] for c in hole_card]))
    lucky_preflop = ['AK', 'KQ', 'QJ', 'JT', 'AQ', 'KJ', 'QT', 'AJ', 'KT', 'AT']
    lucky_preflop = set([''.join(sorted(list(cc))) for cc in lucky_preflop])

    if comb not in lucky_preflop:
        features.loc['lucky_preflop'] = 0
    else:
        features.loc['lucky_preflop'] = 1

    return features


