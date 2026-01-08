#pragma once

#include "Board.hpp"

namespace reversi {

enum class GameResult : int8_t { Ongoing = 0, BlackWins = 1, WhiteWins = -1, Draw = 2 };

class Game {
public:
    Game();

    Move getBestMove(int depth) const;

    const Board& getBoard() const { return board; }
    Player currentPlayer() const { return playerToMove; }

    std::vector<Move> validMoves() const { return board.getValidMoves(playerToMove); }
    bool makeMove(int row, int col);
    void passTurn();
    GameResult result() const;
    std::pair<int, int> score() const { return board.getScore(); }
    void reset();

private:
    Board board;
    Player playerToMove{Player::Black};
    bool previousPlayerPassed{false};
};

} // namespace reversi


