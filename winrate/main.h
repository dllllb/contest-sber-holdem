#include <vector>
#include <string>

void prepare();

float get_winRate(int num_iterations, std::vector<std::string> my_cards,
				  std::vector<std::string> community_card,
				  std::vector<int> _players_folded,
				  int _players_still_in_game);