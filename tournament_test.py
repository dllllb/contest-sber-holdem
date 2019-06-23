import json

from tournament import play_game


def test_play_game():
    with open('small-run.json') as f:
        conf = json.load(f)

    play_game(1, conf)
