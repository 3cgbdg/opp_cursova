from typing import List, Tuple


def evaluate_move(row: int, col: int, before: List[int], after: List[int], player: int, size: int):
    flips = 0
    for r in range(size):
        for c in range(size):
            bi = before[r * size + c]
            ai = after[r * size + c]
            if ai == player and bi != player:
                flips += 1

    corners = {(0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)}
    corner_bonus = 25 if (row, col) in corners else 0

    c_squares = {(0, 1), (1, 0), (0, size - 2), (1, size - 1),
                 (size - 1, 1), (size - 2, 0), (size - 1, size - 2), (size - 2, size - 1)}
    c_penalty = -6 if (row, col) in c_squares else 0

    x_squares = {(1, 1), (1, size - 2), (size - 2, 1), (size - 2, size - 2)}
    x_penalty = -12 if (row, col) in x_squares else 0

    empties_adj = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = row + dr, col + dc
            if 0 <= rr < size and 0 <= cc < size:
                if after[rr * size + cc] == 0:
                    empties_adj += 1
    frontier_penalty = -empties_adj // 3

    score = 3 * flips + corner_bonus + c_penalty + x_penalty + frontier_penalty

    if score >= 25:
        return score, "Excellent", (60, 220, 120)
    if score >= 12:
        return score, "Good", (120, 210, 120)
    if score >= 5:
        return score, "Decent", (200, 200, 120)
    if score >= 1:
        return score, "Okay", (220, 190, 120)
    if score >= -6:
        return score, "Risky", (230, 160, 80)
    return score, "Bad", (230, 80, 80)


