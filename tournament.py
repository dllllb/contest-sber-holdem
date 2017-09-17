import datetime
import pandas as pd
import multiprocessing
from contextlib import closing
from copy import deepcopy
import os
from pypokerengine.api.game import setup_config, start_poker
from random_player import RandomPlayer
from fish_player import FishPlayer
from honest_player import HonestPlayer
from fold_man import FoldMan
# add custom bots
from honest_agressive_bot import HonestAggressivePlayer, HonestAggressiveNumPlayersPlayer
from preflop_lazy_bot import PreflopLazyPlayer
from antifold_player import AntiFoldPlayer
from careful_player import CarefulPlayer

n_jobs = 64
num_games = 256


def play_game(game_no):
    config = setup_config(
        max_round=50,
        initial_stack=1500,
        small_blind_amount=15,
        summary_file=None)

    players = [
        AntiFoldPlayer(),
        HonestAggressiveNumPlayersPlayer(),
        HonestAggressivePlayer(),
        HonestAggressiveNumPlayersPlayer(),
        HonestPlayer(),
        CarefulPlayer(),
        RandomPlayer(),
        FishPlayer(),
        FishPlayer(),
    ]

    for i, pl in enumerate(players):
        config.register_player(name='{}. {}'.format(i, pl.__class__.__name__), algorithm=pl)

    print('Starting game {}'.format(game_no))
    game_result = start_poker(config, verbose=0)
    result = [(p['name'], p['stack']) for p in game_result['players']]

    for name, score in result:
        print('Game #{}, {}: {}'.format(game_no, name, score))

    return result


start_time = datetime.datetime.now()
with closing(multiprocessing.Pool(n_jobs)) as pool:
    args = [(game_no,) for game_no in range(num_games)]
    tasks = [pool.apply_async(play_game, arg) for arg in args]
    game_results = [task.get(999999) for task in tasks]
    game_scores = pd.DataFrame([pd.Series(dict(r)) for r in game_results]).sum().div(num_games)


print('Elapsed time: {}'.format(datetime.datetime.now() - start_time))
print(game_scores)
