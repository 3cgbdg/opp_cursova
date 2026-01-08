#include "Game.hpp"
#include "AI.hpp"

using namespace reversi;

Game::Game() : board(), playerToMove(Player::Black), previousPlayerPassed(false) {}

bool Game::makeMove(int row, int col) {
    if (board.applyMove(playerToMove, row, col)) {
        previousPlayerPassed = false;
        playerToMove = static_cast<Player>(-static_cast<int8_t>(playerToMove));
        return true;
    }
    return false;
}

void Game::passTurn() {
    bool currentPlayerHasNoMoves = board.getValidMoves(playerToMove).empty();
    previousPlayerPassed = currentPlayerHasNoMoves;
    playerToMove = static_cast<Player>(-static_cast<int8_t>(playerToMove));
}

GameResult Game::result() const {
    bool blackHas = board.hasAnyValidMove(Player::Black);
    bool whiteHas = board.hasAnyValidMove(Player::White);
    // Гра закінчується тільки коли обидва гравці не мають ходів
    if (blackHas || whiteHas) return GameResult::Ongoing;
    auto [b, w] = board.getScore();
    if (b > w) return GameResult::BlackWins;
    if (w > b) return GameResult::WhiteWins;
    return GameResult::Draw;
}

void Game::reset() {
    board.reset();
    playerToMove = Player::Black;
    previousPlayerPassed = false;
}

Move Game::getBestMove(int depth) const {
    return AI::getBestMove(board, playerToMove, depth);
}


