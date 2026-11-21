#!/usr/bin/env python3
"""VELARIS — a travel poster for a place that does not exist.

Draws a 768x1024 poster with the Python standard library only.
No fonts, no images, no network: every pixel is computed here and
the PNG is encoded by hand (zlib + struct).

The place: VELARIS, a chain of floating islands above a golden sea,
where waterfalls fall out of the sky and never reach the ground.
"""
import math
import os
import struct
import zlib

W, H = 768, 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- pixels
class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(rgb)

    def blend(self, x, y, rgb, a):
        """Alpha-blend rgb over the pixel at (x, y); a in 0..1."""
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            for k in range(3):
                self.px[i + k] = int(self.px[i + k] * (1 - a) + rgb[k] * a)

    def disc(self, cx, cy, r, rgb, a=1.0):
        r2 = r * r
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                dx, dy = x - cx, y - cy
                d2 = dx * dx + dy * dy
                if d2 <= r2:
                    edge = 1.0 if d2 <= (r - 1) ** 2 else 0.5
                    self.blend(x, y, rgb, a * edge)

    def ellipse(self, cx, cy, rx, ry, rgb, a=1.0):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                dx, dy = (x - cx) / rx, (y - cy) / ry
                if dx * dx + dy * dy <= 1.0:
                    self.blend(x, y, rgb, a)

    def line(self, x0, y0, x1, y1, rgb, width=1, a=1.0):
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        r = width / 2.0
        for s in range(steps + 1):
            t = s / steps
            self.disc(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, rgb, a)

    def poly(self, pts, rgb, width=1, a=1.0, close=False):
        n = len(pts)
        for i in range(n - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      rgb, width, a)
        if close and n > 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1],
                      rgb, width, a)

    def fill_poly(self, pts, rgb, a=1.0):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in pts]
        y0, y1 = int(min(ys)), int(max(ys))
        for y in range(y0, y1 + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, yy1 = pts[i]
                x2, yy2 = pts[(i + 1) % n]
                if (yy1 <= y < yy2) or (yy2 <= y < yy1):
                    t = (y - yy1) / (yy2 - yy1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.blend(x, y, rgb, a)


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ---------------------------------------------------------------- palette
SKY_TOP = (26, 42, 92)       # deep dusk indigo
SKY_MID = (94, 110, 168)     # lavender blue
SKY_LOW = (244, 178, 120)    # warm peach at the horizon
SUN = (255, 214, 140)
SUN_CORE = (255, 240, 200)
SEA_TOP = (232, 150, 96)
SEA_BOT = (38, 62, 110)
ISLAND_ROCK = (74, 58, 74)
ISLAND_GRASS = (58, 128, 92)
ISLAND_DARK = (46, 36, 52)
TOWER = (245, 238, 220)
CREAM = (250, 244, 228)
CLOUD = (250, 236, 214)


def vgrad(c, y, y0, y1, c_top, c_bot):
    t = max(0.0, min(1.0, (y - y0) / (y1 - y0)))
    return lerp(c_top, c_bot, t)


# ---------------------------------------------------------------- scene
def draw_sky(c):
    horizon = 640
    for y in range(horizon):
        if y < 380:
            col = vgrad(None, y, 0, 380, SKY_TOP, SKY_MID)
        else:
            col = vgrad(None, y, 380, horizon, SKY_MID, SKY_LOW)
        for x in range(W):
            c.set(x, y, col)
    # stars in the upper sky
    import random
    rng = random.Random(7)
    for _ in range(90):
        x = rng.randrange(0, W)
        y = rng.randrange(0, 300)
        b = rng.random()
        if b < 0.7:
            c.set(x, y, (255, 255, 255) if b < 0.4 else (200, 210, 255))


def draw_sun(c):
    # a low evening sun, clear of the islands, right of centre.
    # Smooth radial glow: many thin rings fading outward.
    for r in range(150, 52, -2):
        a = 0.22 * (1 - r / 155.0) ** 1.5
        c.disc(590, 400, r, SUN, a)
    c.disc(590, 400, 52, SUN)
    c.disc(590, 400, 40, SUN_CORE)


def draw_sea(c):
    horizon = 640
    for y in range(horizon, H):
        col = vgrad(None, y, horizon, H, SEA_TOP, SEA_BOT)
        for x in range(W):
            c.set(x, y, col)
    # sun reflection: shimmering horizontal streaks under the sun
    import random
    rng = random.Random(21)
    for _ in range(170):
        x = 590 + rng.gauss(0, 80)
        y = rng.randrange(horizon + 8, H - 10)
        w = rng.randrange(14, 70)
        a = rng.uniform(0.08, 0.32)
        for xx in range(int(x - w / 2), int(x + w / 2)):
            c.blend(xx, y, SUN, a)


def draw_cloud(c, cx, cy, s, a=0.85):
    for dx, dy, r in ((-1.1, 0.1, 0.55), (-0.4, -0.25, 0.7), (0.3, 0.05, 0.8),
                      (1.05, 0.15, 0.55), (0.0, 0.3, 0.9)):
        c.ellipse(cx + dx * s, cy + dy * s, r * s, r * s * 0.45, CLOUD, a)


def draw_island(c, cx, top_y, w, h, tower=False):
    """A floating island: grassy top, rocky inverted cone below."""
    # rock body (inverted cone with a rounded tip)
    pts = [(cx - w / 2, top_y), (cx + w / 2, top_y),
           (cx + w * 0.18, top_y + h), (cx, top_y + h + 26),
           (cx - w * 0.18, top_y + h)]
    c.fill_poly(pts, ISLAND_ROCK)
    # shading on the rock
    pts2 = [(cx, top_y), (cx + w / 2, top_y),
            (cx + w * 0.18, top_y + h), (cx, top_y + h + 26)]
    c.fill_poly(pts2, ISLAND_DARK, 0.45)
    # grassy cap
    c.ellipse(cx, top_y, w / 2, 16, ISLAND_GRASS)
    c.ellipse(cx, top_y - 4, w / 2 * 0.92, 12, (76, 152, 108))
    # pine trees
    for tx, th in ((-w * 0.28, 34), (-w * 0.12, 26), (w * 0.22, 30)):
        bx = cx + tx
        c.fill_poly([(bx, top_y - th), (bx - 9, top_y - 4),
                     (bx + 9, top_y - 4)], (34, 96, 66))
        c.line(bx, top_y - 4, bx, top_y + 2, (60, 44, 34), 3)
    if tower:
        # the landmark: a slim white lighthouse tower with a warm lamp
        tx = cx + w * 0.05
        c.fill_poly([(tx - 16, top_y - 118), (tx + 16, top_y - 118),
                     (tx + 11, top_y - 4), (tx - 11, top_y - 4)], TOWER)
        c.fill_poly([(tx - 20, top_y - 118), (tx + 20, top_y - 118),
                     (tx + 14, top_y - 132), (tx - 14, top_y - 132)],
                    (196, 84, 64))
        c.disc(tx, top_y - 148, 12, SUN_CORE)
        c.disc(tx, top_y - 148, 22, SUN, 0.35)
        # a soft beam of lamplight fanning out to the right
        c.fill_poly([(tx + 6, top_y - 152), (tx + 6, top_y - 144),
                     (tx + 130, top_y - 132), (tx + 130, top_y - 164)],
                    SUN, 0.07)
        # red band around the tower
        c.fill_poly([(tx - 14, top_y - 66), (tx + 14, top_y - 66),
                     (tx + 13, top_y - 54), (tx - 13, top_y - 54)],
                    (196, 84, 64))


def draw_waterfall(c, x, y0, y1):
    """A thin waterfall falling off an island edge, fading into mist."""
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0)
        a = 0.85 * (1 - t * 0.55)
        wob = math.sin(y * 0.11) * 2
        c.line(x + wob - 2, y, x + wob + 2, y, (235, 244, 250), 1, a)
    # mist puff where it dissolves
    c.ellipse(x, y1, 26, 10, (250, 244, 230), 0.5)
    c.ellipse(x, y1 + 8, 18, 8, (250, 244, 230), 0.35)


def draw_birds(c):
    for bx, by, s in ((150, 300, 10), (210, 268, 8), (600, 330, 9),
                      (640, 292, 7), (540, 240, 8)):
        c.poly([(bx - s, by), (bx, by - s * 0.6), (bx + s, by)],
               (40, 44, 70), 3)


# ---------------------------------------------------------------- lettering
# Stroke font on a 5 x 7 grid. Each glyph is a list of polylines;
# coordinates are (col, row), col 0..4, row 0..6.
FONT = {
    "V": [[(0, 0), (2, 6), (4, 0)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    "L": [[(0, 0), (0, 6), (4, 6)]],
    "A": [[(0, 6), (2, 0), (4, 6)], [(1, 3.4), (3, 3.4)]],
    "R": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2.4), (3, 3.4), (0, 3.4)],
          [(2, 3.4), (4, 6)]],
    "I": [[(0, 0), (4, 0)], [(2, 0), (2, 6)], [(0, 6), (4, 6)]],
    "S": [[(4, 0.8), (3, 0), (1, 0), (0, 1), (0, 2.4), (1, 3.2),
           (3, 3.2), (4, 4), (4, 5.2), (3, 6), (1, 6), (0, 5.2)]],
}


def draw_text(c, text, cx, y, scale, rgb, spacing=1.6):
    """Draw centred text with the stroke font. Returns text width."""
    unit_w = 5 * scale
    gap = spacing * scale
    total = len(text) * unit_w + (len(text) - 1) * gap
    x = cx - total / 2
    lw = max(2, int(scale * 0.55))
    for ch in text:
        for stroke in FONT.get(ch, []):
            pts = [(x + px * scale, y + py * scale) for px, py in stroke]
            c.poly(pts, rgb, lw)
        x += unit_w + gap
    return total


# ---------------------------------------------------------------- png
def write_png(c, path):
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[y * c.w * 3:(y + 1) * c.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- main
def main():
    c = Canvas(W, H)
    draw_sky(c)
    draw_sun(c)
    # clouds drifting across the sky
    draw_cloud(c, 130, 210, 46, 0.55)
    draw_cloud(c, 640, 170, 54, 0.6)
    draw_cloud(c, 560, 430, 40, 0.45)
    draw_cloud(c, 90, 470, 36, 0.4)
    draw_birds(c)
    # the floating isles of Velaris (main isle carries the lighthouse)
    draw_island(c, 300, 470, 300, 120, tower=True)
    draw_island(c, 560, 540, 210, 90)
    draw_island(c, 120, 560, 150, 70)
    # waterfalls spilling off the islands into the mist
    draw_waterfall(c, 170, 480, 610)
    draw_waterfall(c, 640, 548, 640)
    draw_sea(c)
    # mist where the falls meet the sea
    c.ellipse(170, 645, 60, 14, (250, 244, 230), 0.4)
    c.ellipse(640, 645, 44, 11, (250, 244, 230), 0.35)

    # --- title: the place name, set large at the top ---
    draw_text(c, "VELARIS", W // 2, 78, 13.5, CREAM)
    # thin rule under the name
    c.line(W // 2 - 130, 200, W // 2 + 130, 200, CREAM, 3, 0.9)
    c.disc(W // 2, 200, 5, CREAM)

    n = write_png(c, OUT)
    print(f"wrote {OUT}: {W}x{H}, {n} bytes")


if __name__ == "__main__":
    main()
