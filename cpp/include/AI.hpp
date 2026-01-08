#pragma once

#include "Board.hpp"
#include <vector>
#include <utility>

namespace reversi {

class AI {
public:
    static Move getBestMove(const Board& board, Player player, int depth);

private:
    static int minimax(Board board, int depth, int alpha, int beta, Player maximizingPlayer, Player currentPlayer);
    static int evaluate(const Board& board, Player player);
};

} // namespace reversi
