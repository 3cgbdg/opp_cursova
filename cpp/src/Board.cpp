#include "Board.hpp"

using namespace reversi;

namespace {
constexpr int DIRS[8][2] = {
    {-1, -1}, {-1, 0}, {-1, 1},
    { 0, -1},          { 0, 1},
    { 1, -1}, { 1, 0}, { 1, 1}
};
}

Board::Board() {
    reset();
}

void Board::reset() {
    cells.fill(Cell::Empty);
    int mid = kSize / 2;
    setCell(mid - 1, mid - 1, Cell::White);
    setCell(mid,     mid,     Cell::White);
    setCell(mid - 1, mid,     Cell::Black);
    setCell(mid,     mid - 1, Cell::Black);
}

Cell Board::getCell(int row, int col) const {
    return cells[static_cast<size_t>(row * kSize + col)];
}

void Board::setCell(int row, int col, Cell value) {
    cells[static_cast<size_t>(row * kSize + col)] = value;
}

bool Board::inBounds(int row, int col) {
    return row >= 0 && col >= 0 && row < kSize && col < kSize;
}

bool Board::willFlipInDirection(Player player, int row, int col, int dRow, int dCol) const {
    int r = row + dRow;
    int c = col + dCol;
    Cell me = static_cast<Cell>(static_cast<int8_t>(player));
    Cell opp = static_cast<Cell>(-static_cast<int8_t>(player));
    bool seenOpp = false;
    while (inBounds(r, c) && getCell(r, c) == opp) {
        seenOpp = true;
        r += dRow; c += dCol;
    }
    return seenOpp && inBounds(r, c) && getCell(r, c) == me;
}

std::vector<Move> Board::getValidMoves(Player player) const {
    std::vector<Move> moves;
    for (int r = 0; r < kSize; ++r) {
        for (int c = 0; c < kSize; ++c) {
            if (getCell(r, c) != Cell::Empty) continue;
            bool ok = false;
            for (auto& d : DIRS) {
                if (willFlipInDirection(player, r, c, d[0], d[1])) { ok = true; break; }
            }
            if (ok) moves.push_back({r, c});
        }
    }
    return moves;
}

bool Board::isValidMove(Player player, int row, int col) const {
    if (!inBounds(row, col) || getCell(row, col) != Cell::Empty) return false;
    for (auto& d : DIRS) {
        if (willFlipInDirection(player, row, col, d[0], d[1])) return true;
    }
    return false;
}

int Board::applyDirection(Player player, int row, int col, int dRow, int dCol) {
    int r = row + dRow;
    int c = col + dCol;
    Cell me = static_cast<Cell>(static_cast<int8_t>(player));
    Cell opp = static_cast<Cell>(-static_cast<int8_t>(player));
    int flipped = 0;
    while (inBounds(r, c) && getCell(r, c) == opp) { r += dRow; c += dCol; }
    if (!inBounds(r, c) || getCell(r, c) != me) return 0;
    r -= dRow; c -= dCol;
    while (r != row || c != col) {
        if (getCell(r, c) == opp) { setCell(r, c, me); ++flipped; }
        r -= dRow; c -= dCol;
    }
    return flipped;
}

bool Board::applyMove(Player player, int row, int col) {
    if (!isValidMove(player, row, col)) return false;
    Cell me = static_cast<Cell>(static_cast<int8_t>(player));
    setCell(row, col, me);
    for (auto& d : DIRS) { applyDirection(player, row, col, d[0], d[1]); }
    return true;
}

std::pair<int, int> Board::getScore() const {
    int black = 0, white = 0;
    for (auto cell : cells) {
        if (cell == Cell::Black) ++black;
        else if (cell == Cell::White) ++white;
    }
    return {black, white};
}

bool Board::hasAnyValidMove(Player player) const {
    for (int r = 0; r < kSize; ++r) {
        for (int c = 0; c < kSize; ++c) {
            if (isValidMove(player, r, c)) return true;
        }
    }
    return false;
}


