#include "AI.hpp"
#include <algorithm>
#include <limits>

namespace reversi {

// Position weights
static const int kWeights[8][8] = {
    { 120, -20,  20,   5,   5,  20, -20, 120 },
    { -20, -40,  -5,  -5,  -5,  -5, -40, -20 },
    {  20,  -5,  15,   3,   3,  15,  -5,  20 },
    {   5,  -5,   3,   3,   3,   3,  -5,   5 },
    {   5,  -5,   3,   3,   3,   3,  -5,   5 },
    {  20,  -5,  15,   3,   3,  15,  -5,  20 },
    { -20, -40,  -5,  -5,  -5,  -5, -40, -20 },
    { 120, -20,  20,   5,   5,  20, -20, 120 }
};

Move AI::getBestMove(const Board& board, Player player, int depth) {
    auto moves = board.getValidMoves(player);
    if (moves.empty()) {
        return {-1, -1};
    }

    Move bestMove = moves[0];
    int bestScore = std::numeric_limits<int>::min();
    int alpha = std::numeric_limits<int>::min();
    int beta = std::numeric_limits<int>::max();

    for (const auto& move : moves) {
        Board nextBoard = board; // Copy
        nextBoard.applyMove(player, move.row, move.col);
        
        // Pass the turn to the opponent for the next recursive step
        Player opponent = (player == Player::Black) ? Player::White : Player::Black;
        
        int score = minimax(nextBoard, depth - 1, alpha, beta, player, opponent);
        
        if (score > bestScore) {
            bestScore = score;
            bestMove = move;
        }
        alpha = std::max(alpha, bestScore);
        if (beta <= alpha) {
            break; 
        }
    }

    return bestMove;
}

int AI::minimax(Board board, int depth, int alpha, int beta, Player maximizingPlayer, Player currentPlayer) {
    if (depth == 0) {
        return evaluate(board, maximizingPlayer);
    }

    auto moves = board.getValidMoves(currentPlayer);
    
    // Handle pass case
    if (moves.empty()) {
        Player opponent = (currentPlayer == Player::Black) ? Player::White : Player::Black;
        // Check if game over (opponent also has no moves)
        if (!board.hasAnyValidMove(opponent)) {
            // Game over, return exact score difference heavily weighted
            auto [b, w] = board.getScore();
            int diff = (maximizingPlayer == Player::Black) ? (b - w) : (w - b);
            // Multiply by 1000 to prioritize winning over heuristic
            if (diff > 0) return 10000 + diff;
            if (diff < 0) return -10000 + diff;
            return 0;
        }
        // Pass turn
        return minimax(board, depth, alpha, beta, maximizingPlayer, opponent);
    }

    if (currentPlayer == maximizingPlayer) {
        int maxEval = std::numeric_limits<int>::min();
        for (const auto& move : moves) {
            Board nextBoard = board;
            nextBoard.applyMove(currentPlayer, move.row, move.col);
            Player opponent = (currentPlayer == Player::Black) ? Player::White : Player::Black;
            
            int eval = minimax(nextBoard, depth - 1, alpha, beta, maximizingPlayer, opponent);
            maxEval = std::max(maxEval, eval);
            alpha = std::max(alpha, eval);
            if (beta <= alpha) break;
        }
        return maxEval;
    } else {
        int minEval = std::numeric_limits<int>::max();
        for (const auto& move : moves) {
            Board nextBoard = board;
            nextBoard.applyMove(currentPlayer, move.row, move.col);
            Player opponent = (currentPlayer == Player::Black) ? Player::White : Player::Black;
            
            int eval = minimax(nextBoard, depth - 1, alpha, beta, maximizingPlayer, opponent);
            minEval = std::min(minEval, eval);
            beta = std::min(beta, eval);
            if (beta <= alpha) break;
        }
        return minEval;
    }
}

int AI::evaluate(const Board& board, Player player) {
    int score = 0;
    
    // Positional score
    const auto& cells = board.data();
    for (int r = 0; r < 8; ++r) {
        for (int c = 0; c < 8; ++c) {
            Cell cell = cells[r * 8 + c];
            if (cell == Cell::Empty) continue;
            
            int val = kWeights[r][c];
            if (cell == (player == Player::Black ? Cell::Black : Cell::White)) {
                score += val;
            } else {
                score -= val;
            }
        }
    }
    
    // Mobility (number of moves) bonus
    score += (int)board.getValidMoves(player).size() * 5;
    Player opponent = (player == Player::Black) ? Player::White : Player::Black;
    score -= (int)board.getValidMoves(opponent).size() * 5;

    return score;
}

} // namespace reversi
