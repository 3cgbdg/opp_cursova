from typing import Tuple, Dict
import time


Animation = Dict[str, object]  # keys: pos (Tuple[int,int]), start (float), kind (str)


def new_animation(pos: Tuple[int, int], kind: str) -> Animation:
    return {"pos": pos, "start": time.time(), "kind": kind}


def is_active(anim: Animation, duration: float) -> bool:
    return (time.time() - float(anim["start"])) < duration


