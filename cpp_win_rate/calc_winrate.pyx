from libcpp.string cimport string
from libcpp.vector cimport vector


cdef extern from "main.h":
    void prepare()

    float get_winRate(int num_iterations, vector[string] my_cards,
							 vector[string] community_card,
							 vector[int] _players_folded,
							 int _players_still_in_game)

prepare()

cpdef public float calc(_num_iterations, hole, cc, _players_folded, players_still_in_game):
    winRate = get_winRate(_num_iterations, hole, cc, _players_folded, players_still_in_game)
    return winRate
