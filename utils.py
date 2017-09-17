import json
import pandas as pd, numpy as np
import os
from time import time
import multiprocessing
from contextlib import closing
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate


def get_cards(community_card, street):
    if street == 'preflop':
        return []
    elif street == 'flop':
        return community_card[:3]
    elif street == 'turn':
        return community_card[:4]
    elif street == 'river':
        return community_card[:5]
    
def parse_json(filename):
    with open(filename) as f:
        j = json.loads(f.read())
        
    seats_lst = []
    actions_lst = []
    winners_lst = []
    streets = ['preflop', 'flop', 'turn', 'river']
    for rnd in j['rounds']:
        rnd_no = rnd['round_state']['round_count']
        pot = rnd['round_state']['pot']['main']['amount']
        community_card = rnd['round_state']['community_card']
        state_dct = {}
        for pl in rnd['round_state']['seats']:
            pl['round_count'] = rnd_no
            pl['starting_pot'] = pot
            seats_lst.append(pl)
            state_dct[pl['uuid']] = pl['start_state']

        participating_cnt = sum([x == 'participating' for x in state_dct.values()])
        for street in streets:
            if street in rnd['round_state']['action_histories'].keys():
                act_hist = rnd['round_state']['action_histories'][street]
                for action_count, act in enumerate(act_hist):
                    act['action_count'] = action_count
                    act['round_count'] = rnd_no
                    act['street'] = street
                    act['community_card'] = get_cards(community_card, street)
                    act['nb_player'] = participating_cnt
                    actions_lst.append(act)
                    if act['action'] == 'FOLD':
                        participating_cnt -= 1

        for winner in rnd['winners']:
            winner['round_count'] = rnd_no
            winners_lst.append(winner)

    seats_df = pd.DataFrame(seats_lst)
    seats_df['game'] = filename.split('/')[-1]
    actions_df = pd.DataFrame(actions_lst)
    actions_df['bot_failed'] = actions_df['bot'].dropna().apply(lambda dct: dct['failed'])
    actions_df['bot_time_elapsed'] = actions_df['bot'].dropna().apply(lambda dct: dct['time_elapsed'])
    winner_df = pd.DataFrame(winners_lst).rename(columns={'stack': 'win_stack', 'state': 'win_state'})
    df = actions_df.drop('bot', axis=1).merge(seats_df, how = 'left', on=['round_count', 'uuid'])
    df = df.merge(winner_df, how = 'left', on=['round_count', 'name', 'uuid'])
    df = df.set_index(['game', 'round_count', 'street', 'action_count', 'name', 'uuid']).sort_index().reset_index()
    
    return df


def read_game_day(folder = 'history/tournament_2017-09-15/', n_jobs = 100):
    start_time = time()
    filenames = [(folder+f, ) for f in os.listdir(folder)]
    with closing(multiprocessing.Pool(n_jobs)) as pool:
        tasks = [pool.apply_async(parse_json, f) for f in filenames]
        df_list = [task.get(999999) for task in tasks] 

    games = pd.concat(df_list)
    # counting bluff rate = streets_count_average
    streets_count_average = games.groupby(['game', 'round_count', 'name'])['street'].nunique()\
      .groupby(['name']).mean().to_frame('streets_count_average').reset_index()
    games = games.merge(streets_count_average, how='left', on=['name'])
    
    print(games.shape)
    print(time() - start_time, 'sec')
    return games


def win_rate_calc(df, NB_SIMULATION):
    df['win_rate'] = df.apply(lambda row: estimate_hole_card_win_rate(
                                    nb_simulation=NB_SIMULATION,
                                    nb_player=row['nb_player'],
                                    hole_card=gen_cards(row['hole_card']),
                                    community_card=gen_cards(row['community_card'])
                                    ), axis=1)
    return df
    

def calculate_bluffiness(games_df, games_per_name=100, NB_SIMULATION=100, n_jobs=100):
    start_time = time()
    desicions = games_df.groupby(['name']).head(games_per_name)
    print(desicions.shape[0], 'rows')
    step = 100
    chuncks = []
    for i in range(0, desicions.shape[0], step):
        chuncks.append((desicions.iloc[i:i+step].copy(), NB_SIMULATION))
    print(len(chuncks), 'chunks done')
    with closing(multiprocessing.Pool(n_jobs)) as pool:
        tasks = [pool.apply_async(win_rate_calc, chunk) for chunk in chuncks]
        df_list = [task.get(999999) for task in tasks] 

    win_rate = pd.concat(df_list).reset_index(drop=True)
    print(time() - start_time, 'sec')
    return win_rate

