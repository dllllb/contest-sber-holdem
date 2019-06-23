import datetime
import importlib

import pandas as pd
import numpy as np
import json
import argparse
import multiprocessing
from contextlib import closing

from pypokerengine.api.game import setup_config, start_poker


def play_game(game_no, conf):
    n_players = conf['n_players']

    config = setup_config(
        max_round=conf['max_round'],
        initial_stack=conf['initial_stack'],
        small_blind_amount=conf['small_blind_amount'],
        summary_file=None)

    bots = list()
    for bot in conf['bots']:
        m = importlib.import_module(bot['module'])
        cl = getattr(m, bot['class'])
        props = bot.get('properties', dict())
        bots.append((cl, props))

    players = np.random.choice(len(bots), n_players, replace=False)

    for idx in players:
        pl_cls, pl_props = bots[idx]
        pl = pl_cls(pl_props)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', required=True)
    args = parser.parse_args()

    with open(args.conf) as f:
        conf = json.load(f)

    n_jobs = conf['n_jobs']
    num_games = conf['num_games']

    start_time = datetime.datetime.now()
    with closing(multiprocessing.Pool(n_jobs)) as pool:
        args = [(game_no,) for game_no in range(num_games)]
        tasks = [pool.apply_async(play_game, arg) for arg in args]
        game_results = [task.get(999999) for task in tasks]
        game_scores = pd.DataFrame(game_results).mean()

    print('Elapsed time: {}'.format(datetime.datetime.now() - start_time))
    print(game_scores)
