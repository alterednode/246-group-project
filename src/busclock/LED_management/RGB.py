from __future__ import annotations

num_leds = 106


class RGB:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b


def blank_frame() -> list[RGB]:
    return [RGB(0, 0, 0) for _ in range(num_leds)]


def solid_frame(r: int, g: int, b: int) -> list[RGB]:
    return [RGB(r, g, b) for _ in range(num_leds)]
