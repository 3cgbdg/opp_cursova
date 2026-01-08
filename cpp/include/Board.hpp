#pragma once

#include <array>
#include <vector>
#include <cstdint>

namespace reversi {

enum class Cell : int8_t { Empty = 0, Black = 1, White = -1 };

enum class Player : int8_t { Black = 1, White = -1 };

struct Move {
    int row;
    int col;
};

class Board {
public:
    static constexpr int kSize = 8;

    Board();

    Cell getCell(int row, int col) const;
    void setCell(int row, int col, Cell value);

    std::vector<Move> getValidMoves(Player player) const;
    bool isValidMove(Player player, int row, int col) const;
    bool applyMove(Player player, int row, int col);

    std::pair<int, int> getScore() const;
    bool hasAnyValidMove(Player player) const;

    const std::array<Cell, kSize * kSize>& data() const { return cells; }

    void reset();

private:
    std::array<Cell, kSize * kSize> cells{};

    bool willFlipInDirection(Player player, int row, int col, int dRow, int dCol) const;
    int applyDirection(Player player, int row, int col, int dRow, int dCol);
    static bool inBounds(int row, int col);
};

} // namespace reversi


