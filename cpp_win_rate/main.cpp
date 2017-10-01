#include <string>
#include <vector>
#include <algorithm>
#include <ctime>
#include <fstream>
#include <sstream>
#include <numeric>
#include <random>
#include <map>
#include "unistd.h"
#include <iostream>

using namespace std;

#include "poker_math.h"
#include "bot_functions.h"

const int countHoleCards = 2;
const int countCommunityCards = 5;
const int cardsInDeck = 52;

//vector<Cards> myCards;
//vector<Cards> communityCards;
//vector<Cards> potencialOppCard;

//vector<int> players_folded;
//string uuid;
//int players_still_in_game;

std::default_random_engine generator;


struct MyAction
{
    string typeAction;
    int amount;

    MyAction()
    {

    }

    MyAction(string typeAction, int amount)
    {
        this->typeAction = typeAction;
        this->amount = amount;
    }

    void make()
    {
        cout << typeAction << "\t" << amount << endl;
    }
};


const vector<string> hole_rank_order = {
        "AA", "KK", "QQ", "AKs", "JJ", "AQs", "KQs", "AJs", "KJs", "TT", "AKo",
        "ATs", "QJs", "KTs", "QTs", "JTs", "99", "AQo", "A9s", "KQo", "88",
        "K9s", "T9s", "A8s", "Q9s", "J9s", "AJo", "A5s", "77", "A7s", "KJo",
        "A4s", "A3s", "A6s", "QJo", "66", "K8s", "T8s", "A2s", "98s", "J8s",
        "ATo", "Q8s", "K7s", "KTo", "55", "JTo", "87s", "QTo", "44", "22",
        "33", "K6s", "97s", "K5s", "76s", "T7s", "K4s", "K2s", "K3s", "Q7s",
        "86s", "65s", "J7s", "54s", "Q6s", "75s", "96s", "Q5s", "64s", "Q4s",
        "Q3s", "T9o", "T6s", "Q2s", "A9o", "53s", "85s", "J6s", "J9o", "K9o",
        "J5s", "Q9o", "43s", "74s", "J4s", "J3s", "95s", "J2s", "63s", "A8o",
        "52s", "T5s", "84s", "T4s", "T3s", "42s", "T2s", "98o", "T8o", "A5o",
        "A7o", "73s", "A4o", "32s", "94s", "93s", "J8o", "A3o", "62s", "92s",
        "K8o", "A6o", "87o", "Q8o", "83s", "A2o", "82s", "97o", "72s", "76o",
        "K7o", "65o", "T7o", "K6o", "86o", "54o", "K5o", "J7o", "75o", "Q7o",
        "K4o", "K3o", "96o", "K2o", "64o", "Q6o", "53o", "85o", "T6o", "Q5o",
        "43o", "Q4o", "Q3o", "74o", "Q2o", "J6o", "63o", "J5o", "95o", "52o",
        "J4o", "J3o", "42o", "J2o", "84o", "T5o", "T4o", "32o", "T3o", "73o",
        "T2o", "62o", "94o", "93o", "92o", "83o", "82o", "72o" };

map<string, vector<vector<Cards>>> pair_candidates_map;

struct FastDeck
{
    int cardMask[cardsInDeck];

    std::discrete_distribution<int> distribution;

    void clear()
    {
        vector<int> distribution_weights;
        for (int i = 0; i < cardsInDeck; i++) cardMask[i] = 0;
        for (int j = 0; j < hole_rank_order.size(); j++) {
            distribution_weights.push_back(j);
        }
        distribution = std::discrete_distribution<int>(
                distribution_weights.begin(),distribution_weights.end());
    }
    
    void fixCard(int i) {cardMask[i] = 1;}
    
    int getRandomCard()
    {
        int i;
        while (cardMask[i = rand() % cardsInDeck]) {};
        cardMask[i] = 1;
        return i;
    }


    vector<Cards> getRandomPairFolded(){
        vector<Cards> output;
        while (output.empty()){
            int number = distribution(generator);
            string random_rank = hole_rank_order.at(number);
            vector<vector<Cards>> candidates = pair_candidates_map.at(random_rank);
            random_shuffle(candidates.begin(),candidates.end());
            for (int i = 0; i < candidates.size(); ++i) {
                int val1 = candidates[i][0].getValue();
                int val2 = candidates[i][1].getValue();
                if (!cardMask[val1] && !cardMask[val2]){
                    cardMask[val1] = 1;
                    cardMask[val2] = 1;
                    output = candidates[i];
                    break;
                }
            }
        }
        return output;
    }
};


string calc_hole_rank(vector<Cards> hole_hand){
    int r1 = hole_hand[0].getValue() % 13;
    int s1 = hole_hand[0].getValue() / 13;
    int r2 = hole_hand[1].getValue() % 13;
    int s2 = hole_hand[1].getValue() / 13;

    char mod;

    if (s1 == s2){
        mod = 's';
    } else{
        mod = 'o';
    }

    string str = "";

    if (r1 > r2) {
        str += hole_hand[0].getstring().at(0);
        str += hole_hand[1].getstring().at(0);
        str += mod;
    }
    else if (r1 < r2) {
        str += hole_hand[1].getstring().at(0);
        str += hole_hand[0].getstring().at(0);
        str += mod;
    }
    else {
        str += hole_hand[0].getstring().at(0);
        str += hole_hand[1].getstring().at(0);
    }
    return str;
//    for( int i = 0; i < hole_rank_order.size(); i++ ) {
//        if(hole_rank_order[i] == str) {
//            return i;
//        }
//    }
}

void making_candidate_map(){
    for (int i = 0; i < cardsInDeck; ++i) {
        for (int j = i + 1; j < cardsInDeck; ++j) {
            vector<Cards> temp_pair {i,j}; // call two constructors of Cards
            string rank_pattern = calc_hole_rank(temp_pair);
            pair_candidates_map[rank_pattern].push_back(temp_pair);
        }
    }
}

void prepare(){
	srand(unsigned(time(NULL)));
    InitRankCombination();
    making_candidate_map();
}

float get_winRate(int num_iterations, vector<std::string> my_cards,
                                   std::vector<std::string> community_card,
                                   std::vector<int> players_folded,
                                   int players_still_in_game){
    FastDeck deck;
    deck.clear();
    vector<Cards> myCards;
    myCards.clear();
    for (int m = 0; m < my_cards.size(); ++m)
        myCards.push_back(Cards(my_cards[m]));
    vector<Cards> communityCards;
    communityCards.clear();
    for (int n = 0; n < community_card.size(); ++n)
        communityCards.push_back(Cards(community_card[n]));
    for (int i = 0; i < myCards.size(); i++)
        deck.fixCard(myCards[i].getValue());

    vector<Cards> potencialOppCards;
    vector<Cards> tempVec;
    vector<float> score_result;
    double pointWin = 0;
    int total_players_left = players_still_in_game;

    if (communityCards.size() > 0){
        for (int i = 0; i < communityCards.size(); i++)
            deck.fixCard(communityCards[i].getValue());
        total_players_left += players_folded[1] + players_folded[2] + players_folded[3];
    }

    for (int a = 0; a < num_iterations; a++) {
        potencialOppCards.clear();
        vector<Cards> potentialCommunityCards = communityCards;
        FastDeck tempDeck = deck;
        for (int i = 0; i < countCommunityCards; i++)
            potentialCommunityCards.push_back(tempDeck.getRandomCard());
        for (int j=0; j < players_folded[0]; j++){
            tempVec = tempDeck.getRandomPairFolded();
            potencialOppCards.push_back(tempVec[0]);
            potencialOppCards.push_back(tempVec[1]);
        }
        for (int k = 0; k < total_players_left; ++k) {
            potencialOppCards.push_back(tempDeck.getRandomCard());
            potencialOppCards.push_back(tempDeck.getRandomCard());
        }
        int myVal = combinationF7(potentialCommunityCards, myCards);
        int oppVal;
        score_result.clear();
        double result = -1.0;
        for (int l = 0; l < potencialOppCards.size() / 2; ++l) {
            vector<Cards> sub(&potencialOppCards[l],&potencialOppCards[l + 2]);
            oppVal = combinationF7(potentialCommunityCards, sub);
            if (myVal < oppVal){
                result = 0.0;
                break;
            } else if (myVal > oppVal){
                score_result.push_back(1.0);
            } else{
                score_result.push_back(0.5);
            }
        }
        if (result < 0.0){
            result = std::accumulate(score_result.begin(),score_result.end(), 0.0)/score_result.size();
        }
        pointWin += result;
    }
    return pointWin / (num_iterations);
}