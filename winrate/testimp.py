
from calc_winrate import calc

if __name__ == '__main__':
    hole = [b"CK", b"HK"]

    cc = [b"SQ", b"S3", b"D5", b"D2", b"C4"]
    # cc = [b"H5", b"D2", b"C4"]
    _players_folded = [0, 0, 0, 0]
    players_still_in_game = 1
    print(calc(10000, hole, cc, _players_folded, players_still_in_game))
