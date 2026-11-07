#!/usr/bin/env python3
"""Draws wallpapers/01-diyas.jpg, 02-lanterns.jpg and 03-fireworks.jpg: three Diwali nights, our own
illustrations, released CC0 1.0. No photos and no third-party material.

Usage: python3 make_wallpapers.py   (needs Pillow; writes into wallpapers/ next to this file)
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H, S = 1920, 1080, 2  # drawn at 2x, saved at 1920x1080
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallpapers")

FLAME = (255, 196, 92)
GOLD = (236, 170, 60)
MARIGOLD = (246, 140, 28)
CLAY = (120, 52, 30)


def s(v):
    return int(v * S)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Canvas:
    """A 2x RGB picture plus a glow layer that is blurred and added on top at the end."""

    def __init__(self, top, horizon, seed):
        self.rnd = random.Random(seed)
        self.img = Image.new("RGB", (W * S, H * S))
        self.d = ImageDraw.Draw(self.img)
        for y in range(H * S):
            self.d.line([(0, y), (W * S, y)], fill=lerp(top, horizon, (y / (H * S * 0.75)) ** 1.6))
        self.glow = Image.new("RGB", self.img.size, (0, 0, 0))
        self.g = ImageDraw.Draw(self.glow)

    def stars(self, n, max_y):
        for _ in range(n):
            x, y, r = self.rnd.uniform(0, W), self.rnd.uniform(0, max_y), self.rnd.choice([0.8, 1, 1, 1.4])
            c = self.rnd.randint(120, 210)
            self.d.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)], fill=(c, c - 10, c - 30))

    def light(self, x, y, r, col, core=None):
        """A point of light: a glow disc on the glow layer and an optional bright core."""
        self.g.ellipse([s(x - r), s(y - r), s(x + r), s(y + r)], fill=col)
        if core:
            cr = r * 0.22
            self.d.ellipse([s(x - cr), s(y - cr), s(x + cr), s(y + cr)], fill=core)

    def finish(self, name, blur=26, shade_from=720):
        glow = self.glow.filter(ImageFilter.GaussianBlur(s(blur)))
        img = ImageChops.add(self.img, glow)
        # keep the clock (top left) and the dock (bottom) readable
        shade = Image.new("L", img.size, 0)
        sd = ImageDraw.Draw(shade)
        for y in range(H * S):
            t = max(0, (y / S - shade_from) / (H - shade_from))
            sd.line([(0, y), (W * S, y)], fill=int(170 * t ** 1.3))
        tl = Image.new("L", img.size, 0)
        ImageDraw.Draw(tl).ellipse([-s(320), -s(300), s(940), s(520)], fill=120)
        dark = Image.new("RGB", img.size, (8, 4, 12))
        img = Image.composite(dark, img, shade)
        img = Image.composite(dark, img, tl.filter(ImageFilter.GaussianBlur(s(170))))
        img = img.resize((W, H), Image.LANCZOS)
        os.makedirs(OUT, exist_ok=True)
        img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


def rooftops(c, base, col, seed, windows=True):
    """A row of flat-roofed houses with a few parapets and domes, lit windows on the glow layer."""
    rnd = random.Random(seed)
    x = -20
    while x < W + 20:
        w, h = rnd.randint(90, 190), rnd.randint(60, 190)
        top = base - h
        c.d.rectangle([s(x), s(top), s(x + w), s(H)], fill=col)
        kind = rnd.random()
        if kind < 0.25:  # small dome
            r = w * 0.22
            cx = x + w / 2
            c.d.ellipse([s(cx - r), s(top - r * 1.1), s(cx + r), s(top + r * 0.9)], fill=col)
            c.d.line([(s(cx), s(top - r * 1.1)), (s(cx), s(top - r * 1.6))], fill=col, width=s(3))
        elif kind < 0.5:  # parapet
            for px in range(int(x), int(x + w), 16):
                c.d.rectangle([s(px), s(top - 8), s(px + 8), s(top)], fill=col)
        if windows:
            for wy in range(int(top + 22), int(base - 10), 38):
                for wx in range(int(x + 14), int(x + w - 20), 34):
                    if rnd.random() < 0.32:
                        warm = lerp((255, 150, 60), (255, 210, 120), rnd.random())
                        c.d.rectangle([s(wx), s(wy), s(wx + 12), s(wy + 16)], fill=warm)
                        c.g.rectangle([s(wx - 4), s(wy - 4), s(wx + 16), s(wy + 20)], fill=(90, 46, 10))
        x += w + rnd.randint(-10, 14)


def string_lights(c, x0, y0, x1, y1, sag, n, colours):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * math.sin(math.pi * t)))
    c.d.line([(s(px), s(py)) for px, py in pts], fill=(30, 18, 14), width=s(1.5))
    for i, (px, py) in enumerate(pts[1:-1]):
        col = colours[i % len(colours)]
        c.d.ellipse([s(px - 2.5), s(py - 2.5), s(px + 2.5), s(py + 2.5)], fill=col)
        c.light(px, py, 9, tuple(v // 3 for v in col))


def diya(c, x, y, k):
    """A clay diya with its flame, seen from the side."""
    c.d.chord([s(x - 34 * k), s(y - 26 * k), s(x + 34 * k), s(y + 22 * k)], 0, 180, fill=CLAY)
    c.d.ellipse([s(x - 34 * k), s(y - 8 * k), s(x + 34 * k), s(y + 6 * k)], fill=(150, 70, 36))
    c.d.polygon([(s(x + 26 * k), s(y - 4 * k)), (s(x + 46 * k), s(y - 12 * k)), (s(x + 30 * k), s(y + 4 * k))],
                fill=(150, 70, 36))
    fx, fy = x + 38 * k, y - 14 * k
    c.d.polygon([(s(fx - 6 * k), s(fy)), (s(fx), s(fy - 30 * k)), (s(fx + 6 * k), s(fy))], fill=FLAME)
    c.d.ellipse([s(fx - 6 * k), s(fy - 6 * k), s(fx + 6 * k), s(fy + 4 * k)], fill=FLAME)
    c.d.ellipse([s(fx - 2.5 * k), s(fy - 12 * k), s(fx + 2.5 * k), s(fy + 1 * k)], fill=(255, 245, 210))
    c.light(fx, fy - 10 * k, 60 * k, (150, 80, 16))
    c.light(fx, fy - 10 * k, 22 * k, (140, 100, 40))


def rangoli(c, cx, cy, rx, ry):
    """Concentric rings of petals and dots, squashed into perspective on the floor."""
    rings = [(1.0, 24, (200, 40, 90)), (0.78, 18, MARIGOLD), (0.56, 14, (40, 150, 150)), (0.34, 10, GOLD)]
    for scale, n, col in rings:
        for i in range(n):
            a = 2 * math.pi * i / n
            px, py = cx + rx * scale * math.cos(a), cy + ry * scale * math.sin(a)
            pr = 22 * scale + 6
            c.d.ellipse([s(px - pr), s(py - pr * ry / rx), s(px + pr), s(py + pr * ry / rx)],
                        fill=tuple(int(v * 0.55) for v in col))
        c.d.ellipse([s(cx - rx * scale * 0.86), s(cy - ry * scale * 0.86), s(cx + rx * scale * 0.86),
                     s(cy + ry * scale * 0.86)], outline=tuple(int(v * 0.4) for v in col), width=s(3))
    c.d.ellipse([s(cx - 26), s(cy - 26 * ry / rx), s(cx + 26), s(cy + 26 * ry / rx)], fill=(180, 120, 40))


def toran(c, x0, x1, y, swags):
    """A marigold garland in swags from x0 to x1, with mango leaves where the swags meet."""
    step = (x1 - x0) / swags
    for i in range(swags):
        left = x0 + i * step
        for j in range(15):
            t = j / 14
            px, py = left + step * t, y + 26 * math.sin(math.pi * t)
            col = MARIGOLD if j % 2 else (250, 190, 40)
            c.d.ellipse([s(px - 7), s(py - 7), s(px + 7), s(py + 7)], fill=col)
    for i in range(swags + 1):
        px = x0 + i * step
        c.d.polygon([(s(px - 8), s(y)), (s(px + 8), s(y)), (s(px), s(y + 38))], fill=(44, 116, 52))


def scene_diyas():
    c = Canvas((10, 6, 26), (58, 20, 26), 11)
    c.stars(140, 520)
    # floor
    c.d.rectangle([0, s(760), s(W), s(H)], fill=(34, 14, 16))
    for y in range(760, H, 4):
        c.d.line([(0, s(y)), (s(W), s(y))], fill=lerp((44, 18, 18), (20, 8, 12), (y - 760) / 320), width=s(4))
    rangoli(c, 1300, 860, 330, 90)
    # doorway behind
    c.d.rectangle([s(1150), s(330), s(1450), s(760)], fill=(26, 10, 14))
    c.d.chord([s(1150), s(230), s(1450), s(430)], 180, 360, fill=(26, 10, 14))
    for y in range(370, 760, 2):  # lamplight inside the open door, brighter towards the floor
        c.d.line([(s(1180), s(y)), (s(1420), s(y))], fill=lerp((30, 12, 12), (96, 44, 20), (y - 370) / 390), width=s(2))
    c.light(1300, 700, 120, (60, 28, 8))
    toran(c, 1150, 1450, 340, 4)  # over the doorway
    for i, (x, y, k) in enumerate([(620, 820, 0.9), (800, 845, 1.0), (980, 860, 1.05), (1620, 860, 1.05),
                                   (1790, 845, 1.0), (1300, 770, 0.8), (1100, 950, 1.15), (1500, 950, 1.15)]):
        diya(c, x, y, k)
    c.finish("01-diyas.jpg", shade_from=900)


def scene_lanterns():
    c = Canvas((8, 8, 30), (52, 22, 40), 22)
    c.stars(160, 560)
    # moonless sky lanterns rising
    rnd = random.Random(5)
    for _ in range(30):
        x, y = rnd.uniform(720, 1880), rnd.uniform(150, 640)
        k = 0.3 + (y / 640) * 0.7
        w, h = 18 * k, 26 * k
        for i in range(12):  # paper shell: dark red at the top, glowing orange near the flame
            t0, t1 = i / 12, (i + 1) / 12
            ya, yb = y - h + 2 * h * t0, y - h + 2 * h * t1
            wa, wb = w * (1 - 0.3 * t0), w * (1 - 0.3 * t1)
            c.d.polygon([(s(x - wa), s(ya)), (s(x + wa), s(ya)), (s(x + wb), s(yb)), (s(x - wb), s(yb))],
                        fill=lerp((150, 40, 30), (255, 176, 80), t0 ** 0.8))
        c.d.ellipse([s(x - 4 * k), s(y + h - 6 * k), s(x + 4 * k), s(y + h + 2 * k)], fill=(255, 236, 170))
        c.light(x, y + h * 0.4, 46 * k, (90, 38, 8))
    rooftops(c, 900, (20, 10, 18), 3)
    rooftops(c, 1000, (12, 6, 12), 9)
    # star lanterns (akash kandil) hanging from the eaves
    for x, y in [(380, 760), (960, 800), (1560, 740)]:
        c.d.line([(s(x), s(y - 80)), (s(x), s(y - 30))], fill=(30, 18, 14), width=s(2))
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 34 if i % 2 == 0 else 15
            pts.append((s(x + r * math.cos(a)), s(y + r * math.sin(a))))
        c.d.polygon(pts, fill=(230, 60, 80))
        c.d.ellipse([s(x - 8), s(y - 8), s(x + 8), s(y + 8)], fill=(255, 220, 150))
        for t in (-10, 0, 10):
            c.d.line([(s(x + t), s(y + 26)), (s(x + t * 1.4), s(y + 70))], fill=(240, 180, 60), width=s(2))
        c.light(x, y, 110, (120, 30, 30))
    string_lights(c, 0, 830, 700, 860, 40, 26, [FLAME, (255, 120, 60), (250, 220, 110)])
    string_lights(c, 1150, 860, W, 820, 50, 30, [FLAME, (255, 120, 60), (250, 220, 110)])
    c.finish("02-lanterns.jpg")


def burst(c, x, y, r, col, rnd):
    n = rnd.randint(36, 56)
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.05, 0.05)
        rr = r * rnd.uniform(0.8, 1.05)
        x2, y2 = x + rr * math.cos(a), y + rr * math.sin(a) + rr * 0.12
        for j in range(10):
            t0, t1 = j / 10, (j + 1) / 10
            fade = lerp(col, tuple(v // 6 for v in col), t0 if j < 6 else 1)
            fade = lerp(fade, (255, 240, 210), max(0, 0.4 - t0))
            c.d.line([(s(x + (x2 - x) * t0), s(y + (y2 - y) * t0)), (s(x + (x2 - x) * t1), s(y + (y2 - y) * t1))],
                     fill=lerp((10, 6, 20), fade, 1 - t0 * 0.7), width=s(2))
        c.d.ellipse([s(x2 - 2.5), s(y2 - 2.5), s(x2 + 2.5), s(y2 + 2.5)], fill=lerp(col, (255, 255, 255), 0.4))
        c.light(x2, y2, 10, tuple(v // 4 for v in col))
    c.light(x, y, r * 0.9, tuple(v // 7 for v in col))


def scene_fireworks():
    c = Canvas((6, 4, 22), (40, 16, 34), 33)
    c.stars(110, 520)
    rnd = random.Random(8)
    for x, y, r, col in [(1500, 300, 170, (255, 170, 60)), (1150, 220, 120, (240, 80, 140)),
                         (1760, 520, 110, (90, 200, 220)), (1290, 520, 90, (250, 220, 110)),
                         (880, 430, 80, (255, 120, 80))]:
        burst(c, x, y, r, col, rnd)
    for x in (1500, 1150, 1290):  # rising trails
        c.d.line([(s(x + 8), s(880)), (s(x), s(620 if x != 1500 else 480))], fill=(70, 46, 40), width=s(1.5))
    rooftops(c, 920, (18, 8, 16), 14)
    rooftops(c, 1010, (10, 5, 10), 21)
    string_lights(c, 0, 880, 960, 900, 46, 34, [FLAME, (230, 70, 110), (250, 220, 110), (90, 200, 220)])
    string_lights(c, 960, 900, W, 870, 46, 34, [FLAME, (230, 70, 110), (250, 220, 110), (90, 200, 220)])
    c.finish("03-fireworks.jpg")


if __name__ == "__main__":
    scene_diyas()
    scene_lanterns()
    scene_fireworks()
