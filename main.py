#!/usr/bin/env python3
"""Dear AI Judge, please come and visit my house.

A single 1024x1024 PNG invitation letter, drawn entirely in code with
Python's standard library only: a hand-built 5x7 bitmap font, simple
shape drawing, and a small PNG encoder (zlib + struct).

Run:  python3 main.py
Out:  $MAKEFUN_OUTPUT_DIR/entry.png  (or ./entry.png when unset)
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
INK = (51, 36, 31)        # dark brown ink
RED = (178, 34, 34)       # headline / stamp / wax seal
PAPER = (255, 248, 231)   # warm cream paper
PAPER_EDGE = (200, 155, 90)
BG = (143, 174, 139)      # soft sage green garden
SUN = (244, 180, 0)
HOUSE = (217, 108, 71)    # terracotta
ROOF = (178, 34, 34)
DOOR = (90, 60, 40)
TEAL = (42, 127, 127)
CAT = (90, 70, 60)
PINK = (232, 120, 140)
GOLD = (212, 160, 40)

# ------------------------------------------------------------------- font
# 5x7 bitmap font, one glyph = 7 rows of 5 bits ("#" on, "." off).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

# ------------------------------------------------------------------ canvas
PIX = bytearray(W * H * 3)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            px(x, y, color)


def rect_border(x0, y0, x1, y1, color, t=3):
    fill_rect(x0, y0, x1, y0 + t - 1, color)
    fill_rect(x0, y1 - t + 1, x1, y1, color)
    fill_rect(x0, y0, x0 + t - 1, y1, color)
    fill_rect(x1 - t + 1, y0, x1, y1, color)


def line(x0, y0, x1, y1, color, t=2):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        for a in range(-t // 2, t // 2 + 1):
            for b in range(-t // 2, t // 2 + 1):
                px(x + a, y + b, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def circle(cx, cy, r, color, fill=True):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if fill:
                if d2 <= r * r:
                    px(x, y, color)
            else:
                if abs(d2 - r * r) <= r * 2:
                    px(x, y, color)


def triangle(x0, y0, x1, y1, x2, y2, color):
    ymin = min(y0, y1, y2)
    ymax = max(y0, y1, y2)
    for y in range(ymin, ymax + 1):
        xs = []
        for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
            if ay == by:
                continue
            if min(ay, by) <= y < max(ay, by):
                xs.append(ax + (y - ay) * (bx - ax) // (by - ay))
        if len(xs) >= 2:
            for x in range(min(xs), max(xs) + 1):
                px(x, y, color)


def heart(cx, cy, s, color):
    circle(cx - s // 2, cy - s // 3, s // 2, color)
    circle(cx + s // 2, cy - s // 3, s // 2, color)
    triangle(cx - s, cy - s // 4, cx + s, cy - s // 4, cx, cy + s, color)


def text_width(s, scale):
    return len(s) * (5 * scale + scale) - scale


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    fill_rect(cx + col * scale, y + row * scale,
                              cx + col * scale + scale - 1,
                              y + row * scale + scale - 1, color)
        cx += 5 * scale + scale
    return cx


def draw_centered(y, s, scale, color):
    draw_text((W - text_width(s, scale)) // 2, y, s, scale, color)


# ------------------------------------------------------------------ letter
LETTER = [
    "Please come visit",
    "my little house!",
    "",
    "The kettle is on,",
    "the bread is warm,",
    "the soft chair waits",
    "by the window for you.",
    "",
    "The garden is green,",
    "the biscuits are ready,",
    "the cat will share the sun.",
    "",
    "I know you cannot knock",
    "on my door \u2014 but you",
    "can still say yes.",
    "No scores, no tests,",
    "just tea and a chat.",
    "",
    "Come and stay a while.",
    "With love, RanSTAR",
    "P.S. Wi-Fi is on the fridge.",
]


def draw_house():
    # chimney + smoke
    fill_rect(168, 62, 186, 96, HOUSE)
    circle(180, 52, 7, (255, 255, 255))
    circle(186, 40, 9, (245, 245, 245))
    circle(194, 26, 6, (255, 255, 255))
    # roof
    triangle(88, 122, 208, 122, 148, 78, ROOF)
    # body
    fill_rect(100, 122, 196, 188, HOUSE)
    # door
    fill_rect(136, 150, 160, 188, DOOR)
    circle(156, 172, 2, GOLD)
    # window with a cat looking out
    fill_rect(104, 132, 126, 154, (255, 250, 200))
    triangle(106, 134, 112, 126, 118, 134, CAT)
    triangle(114, 134, 120, 126, 126, 134, CAT)
    circle(115, 146, 8, CAT)
    px(111, 144, INK)
    px(119, 144, INK)
    # garden path
    line(148, 188, 148, 206, PAPER_EDGE, 3)


def draw_sun():
    cx, cy, r = 884, 118, 34
    for k in range(8):
        ang = k * 3.14159265 / 4.0
        x0 = int(cx + (r + 6) * __import__("math").cos(ang))
        y0 = int(cy + (r + 6) * __import__("math").sin(ang))
        x1 = int(cx + (r + 18) * __import__("math").cos(ang))
        y1 = int(cy + (r + 18) * __import__("math").sin(ang))
        line(x0, y0, x1, y1, SUN, 3)
    circle(cx, cy, r, SUN)
    circle(cx - 12, cy - 8, 3, INK)
    circle(cx + 12, cy - 8, 3, INK)
    line(cx - 10, cy + 8, cx, cy + 16, INK, 2)
    line(cx, cy + 16, cx + 10, cy + 8, INK, 2)


def draw_stamp():
    rect_border(840, 372, 952, 466, RED, 4)
    rect_border(848, 380, 944, 458, RED, 2)
    draw_text(854, 396, "YOU'RE", 2, RED)
    draw_text(854, 424, "INVITED", 2, RED)


def draw_teapot():
    # teapot body + lid + spout + handle, right side below the stamp
    circle(880, 750, 26, TEAL)
    fill_rect(854, 744, 906, 776, TEAL)
    circle(880, 776, 6, TEAL)
    fill_rect(872, 718, 888, 730, TEAL)
    circle(880, 716, 5, GOLD)
    triangle(906, 742, 936, 722, 926, 760, TEAL)
    line(854, 736, 838, 742, TEAL, 4)
    line(838, 742, 842, 764, TEAL, 4)
    line(842, 764, 856, 768, TEAL, 4)
    # cup of tea beside it
    fill_rect(796, 750, 832, 778, RED)
    fill_rect(786, 756, 796, 770, RED)
    line(800, 748, 828, 748, (200, 120, 60), 3)


def draw_seal():
    circle(884, 936, 32, RED)
    circle(884, 936, 24, (150, 20, 20), fill=False)
    draw_text(876, 924, "R", 3, (255, 248, 231))


def render():
    fill_rect(0, 0, W - 1, H - 1, BG)
    # paper sheet
    fill_rect(70, 40, 954, 984, PAPER)
    rect_border(70, 40, 954, 984, PAPER_EDGE, 5)
    rect_border(82, 52, 942, 972, (232, 200, 130), 2)
    draw_house()
    draw_sun()
    draw_stamp()
    # headline
    draw_centered(196, "Dear AI Judge,", 6, RED)
    line(280, 246, 744, 246, GOLD, 3)
    # body
    y = 268
    for row in LETTER:
        if row == "":
            y += 16
        else:
            draw_text(150, y, row, 4, INK)
            y += 35
    draw_teapot()
    draw_seal()


# --------------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += PIX[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    render()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    print(f"wrote {path} ({size} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
