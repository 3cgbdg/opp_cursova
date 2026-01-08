import ctypes
import os
import sys
from ctypes import c_int, c_int8, c_void_p, POINTER


class ReversiCore:
    def __init__(self, dll_path: str = None):
        dll_candidates = []
        if dll_path:
            dll_candidates.append(dll_path)
        # Next to this file
        dll_dir = os.path.dirname(os.path.abspath(__file__))
        dll_candidates.append(os.path.join(dll_dir, "reversi_core.dll"))
        # Common build outputs
        project_root = os.path.abspath(os.path.join(dll_dir, os.pardir))
        dll_candidates.append(os.path.join(project_root, "build", "Release", "reversi_core.dll"))
        dll_candidates.append(os.path.join(project_root, "build", "reversi_core.dll"))

        load_error = None
        lib = None
        for cand in dll_candidates:
            if not os.path.isfile(cand):
                continue
            try:
                # Ensure directory is on DLL search path (Windows 10+)
                try:
                    if hasattr(os, 'add_dll_directory'):
                        os.add_dll_directory(os.path.dirname(cand))
                except Exception:
                    pass
                lib = ctypes.WinDLL(cand) if os.name == "nt" else ctypes.CDLL(cand)
                dll_path = cand
                break
            except OSError as e:
                load_error = e
                continue

        if lib is None:
            details = [f"tried: {p}" for p in dll_candidates]
            arch = 64 if sys.maxsize > 2**32 else 32
            raise RuntimeError(
                "Failed to load reversi_core DLL. "
                + (f"Last error: {load_error}\n" if load_error else "")
                + "\n".join(details)
                + f"\nPython arch: {arch}-bit"
            )

        self.lib = lib

        self.lib.create_game.restype = c_void_p
        self.lib.destroy_game.argtypes = [c_void_p]

        self.lib.get_board_size.restype = c_int
        self.lib.get_cell.argtypes = [c_void_p, c_int, c_int]
        self.lib.get_cell.restype = c_int
        self.lib.get_board.argtypes = [c_void_p, POINTER(c_int8)]

        self.lib.current_player.argtypes = [c_void_p]
        self.lib.current_player.restype = c_int

        self.lib.get_valid_moves.argtypes = [c_void_p, POINTER(c_int), c_int]
        self.lib.get_valid_moves.restype = c_int

        self.lib.make_move.argtypes = [c_void_p, c_int, c_int]
        self.lib.make_move.restype = c_int

        self.lib.pass_turn.argtypes = [c_void_p]

        self.lib.get_score.argtypes = [c_void_p, POINTER(c_int), POINTER(c_int)]
        self.lib.get_result.argtypes = [c_void_p]
        self.lib.get_result.restype = c_int
        self.lib.reset_game.argtypes = [c_void_p]

        self.lib.get_best_move.argtypes = [c_void_p, c_int]
        self.lib.get_best_move.restype = c_int

        self.handle = self.lib.create_game()
        if not self.handle:
            raise RuntimeError("Failed to create game handle")

        self.size = self.lib.get_board_size()

    def __del__(self):
        try:
            if getattr(self, "handle", None):
                self.lib.destroy_game(self.handle)
                self.handle = None
        except Exception:
            pass

    @staticmethod
    def _resolve_default_path() -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        name = "reversi_core.dll" if os.name == "nt" else "libreversi_core.so"
        return os.path.join(base, name)

    def get_board(self):
        buf = (c_int8 * (self.size * self.size))()
        self.lib.get_board(self.handle, buf)
        return [int(buf[i]) for i in range(self.size * self.size)]

    def get_cell(self, r: int, c: int) -> int:
        return int(self.lib.get_cell(self.handle, r, c))

    def current_player(self) -> int:
        return int(self.lib.current_player(self.handle))

    def valid_moves(self):
        temp = (c_int * 60)()  # max possible moves < 60
        count = self.lib.get_valid_moves(self.handle, temp, 60)
        moves = []
        for i in range(count):
            v = int(temp[i])
            moves.append((v // self.size, v % self.size))
        return moves

    def make_move(self, r: int, c: int) -> bool:
        return bool(self.lib.make_move(self.handle, r, c))

    def pass_turn(self):
        self.lib.pass_turn(self.handle)

    def score(self):
        b = c_int()
        w = c_int()
        self.lib.get_score(self.handle, ctypes.byref(b), ctypes.byref(w))
        return int(b.value), int(w.value)

    def result(self) -> int:
        return int(self.lib.get_result(self.handle))

    def reset(self):
        self.lib.reset_game(self.handle)

    def get_best_move(self, depth: int) -> Tuple[int, int]:
        val = int(self.lib.get_best_move(self.handle, depth))
        if val < 0:
            return (-1, -1)
        return (val // self.size, val % self.size)


    