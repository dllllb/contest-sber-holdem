import datetime
import pandas as pd
import numpy as np
import multiprocessing
from contextlib import closing

from pypokerengine.api.game import setup_config, start_poker
from bots.random_player import RandomPlayer
from bots.fish_player import FishPlayer
from bots.honest_player import HonestPlayer
from bots.fold_man import FoldMan
# add custom bots
from bots.honest_agressive_bot import HonestAggressivePlayer
from bots.preflop_lazy_bot import PreflopLazyPlayer
from bots.honest_minmax_player import HonestMinMaxPlayer
from bots.careful_player import CarefulPlayer

n_jobs = 1
num_games = 2


def play_game(game_no):
    config = setup_config(
        max_round=50,
        initial_stack=1500,
        small_blind_amount=15,
        summary_file=None)

    possible_players = [
        HonestMinMaxPlayer,
        HonestAggressivePlayer,
        PreflopLazyPlayer,
        HonestPlayer,
        CarefulPlayer,
        RandomPlayer,
        FishPlayer,
        FoldMan,
    ]

    players = np.random.choice(possible_players*3, 9, replace=False)

    for i, pl_cls in enumerate(players):
        pl = pl_cls()
        config.register_player(name=pl.__class__.__name__, algorithm=pl)

    print('Starting game {}'.format(game_no))
    game_result = start_poker(config, verbose=0)
    pre_result = dict()
    for p in game_result['players']:
        nm = p['name']
        stack = p['stack']
        if nm in pre_result:
            pre_result[nm] = (pre_result[nm][0] + stack, pre_result[nm][1] + 1)
        else:
            pre_result[nm] = (stack, 1)

    result = dict((nm, stat[0]/float(stat[1])) for nm, stat in pre_result.items())

    for name, score in result.items():
        print('Game #{}, {}: {}'.format(game_no, name, score))

    return result


start_time = datetime.datetime.now()
with closing(multiprocessing.Pool(n_jobs)) as pool:
    args = [(game_no,) for game_no in range(num_games)]
    tasks = [pool.apply_async(play_game, arg) for arg in args]
    game_results = [task.get(999999) for task in tasks]
    game_scores = pd.DataFrame(game_results).mean()


print('Elapsed time: {}'.format(datetime.datetime.now() - start_time))
print(game_scores)
