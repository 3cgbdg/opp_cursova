#pragma once

#ifdef _WIN32
  #ifdef reversi_core_EXPORTS
    #define REVERSI_API __declspec(dllexport)
  #else
    #define REVERSI_API __declspec(dllimport)
  #endif
#else
  #define REVERSI_API
#endif

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void* reversi_handle; // opaque pointer to Game

typedef enum {
    CELL_EMPTY = 0,
    CELL_BLACK = 1,
    CELL_WHITE = -1
} cell_t;

typedef enum {
    PLAYER_BLACK = 1,
    PLAYER_WHITE = -1
} player_t;

typedef enum {
    RESULT_ONGOING = 0,
    RESULT_BLACK = 1,
    RESULT_WHITE = -1,
    RESULT_DRAW = 2
} result_t;

REVERSI_API reversi_handle create_game();
REVERSI_API void destroy_game(reversi_handle h);

REVERSI_API int get_board_size(); // always 8
REVERSI_API cell_t get_cell(reversi_handle h, int row, int col);
REVERSI_API void get_board(reversi_handle h, int8_t* out64);

REVERSI_API player_t current_player(reversi_handle h);
REVERSI_API int get_valid_moves(reversi_handle h, int* out_moves, int max_moves); // returns count; moves as row*8+col
REVERSI_API int make_move(reversi_handle h, int row, int col); // returns 1 if move made
REVERSI_API void pass_turn(reversi_handle h);

REVERSI_API void get_score(reversi_handle h, int* out_black, int* out_white);
REVERSI_API result_t get_result(reversi_handle h);
REVERSI_API void reset_game(reversi_handle h);

REVERSI_API int get_best_move(reversi_handle h, int depth); // Returns row * size + col, or -1

#ifdef __cplusplus
}
#endif


