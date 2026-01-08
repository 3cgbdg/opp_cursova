    #include "api.h"
    #include "Game.hpp"
    #include <vector>
    #include <memory>

    using reversi::Game;
    using reversi::Board;
    using reversi::Player;
    using reversi::GameResult;
    using reversi::Cell;

    extern "C" {

    REVERSI_API reversi_handle create_game() {
        return reinterpret_cast<reversi_handle>(new Game());
    }

    REVERSI_API void destroy_game(reversi_handle h) {
        if (!h) return;
        auto* g = reinterpret_cast<Game*>(h);
        delete g;
    }

    REVERSI_API int get_board_size() { return Board::kSize; }

    REVERSI_API cell_t get_cell(reversi_handle h, int row, int col) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return CELL_EMPTY;
        auto c = g->getBoard().getCell(row, col);
        if (c == Cell::Black) return CELL_BLACK;
        if (c == Cell::White) return CELL_WHITE;
        return CELL_EMPTY;
    }

    REVERSI_API void get_board(reversi_handle h, int8_t* out64) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g || !out64) return;
        const auto& arr = g->getBoard().data();
        for (size_t i = 0; i < arr.size(); ++i) out64[i] = static_cast<int8_t>(arr[i]);
    }

    REVERSI_API player_t current_player(reversi_handle h) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return PLAYER_BLACK;
        return static_cast<player_t>(static_cast<int8_t>(g->currentPlayer()));
    }

    REVERSI_API int get_valid_moves(reversi_handle h, int* out_moves, int max_moves) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return 0;
        auto moves = g->validMoves();
        int n = static_cast<int>(moves.size());
        int toCopy = (out_moves && max_moves > 0) ? std::min(n, max_moves) : 0;
        for (int i = 0; i < toCopy; ++i) {
            out_moves[i] = moves[i].row * Board::kSize + moves[i].col;
        }
        return n;
    }

    REVERSI_API int make_move(reversi_handle h, int row, int col) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return 0;
        return g->makeMove(row, col) ? 1 : 0;
    }

    REVERSI_API void pass_turn(reversi_handle h) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return;
        g->passTurn();
    }

    REVERSI_API void get_score(reversi_handle h, int* out_black, int* out_white) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) { if (out_black) *out_black = 0; if (out_white) *out_white = 0; return; }
        auto s = g->score();
        if (out_black) *out_black = s.first;
        if (out_white) *out_white = s.second;
    }

    REVERSI_API result_t get_result(reversi_handle h) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return RESULT_ONGOING;
        auto r = g->result();
        switch (r) {
            case GameResult::Ongoing: return RESULT_ONGOING;
            case GameResult::BlackWins: return RESULT_BLACK;
            case GameResult::WhiteWins: return RESULT_WHITE;
            case GameResult::Draw: return RESULT_DRAW;
        }
        return RESULT_ONGOING;
    }

    REVERSI_API void reset_game(reversi_handle h) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return;
        g->reset();
    }

    REVERSI_API int get_best_move(reversi_handle h, int depth) {
        auto* g = reinterpret_cast<Game*>(h);
        if (!g) return -1;
        auto move = g->getBestMove(depth);
        if (move.row == -1) return -1;
        return move.row * Board::kSize + move.col;
    }

    }


