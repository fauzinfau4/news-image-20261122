# news-image-20261122 -- "Sunday 22 November 2026: the world in one day"
# Original program, written for the make.fun news-image-20261122 bounty.
# Draws a newspaper front page summing up Sunday 22 November 2026
# with a hand-written 5x7 bitmap font and a pure-stdlib PNG encoder.
# Runs offline, stdlib only, deterministic: the same bytes every run.
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# Hand-written 5x7 pixel font. Each glyph is 7 rows of 5 bits ('1' = ink).
# One blank column is added between glyphs when drawing.
FONT = {
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ',': ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# --------------------------------------------------------------- canvas ----
PAPER = (250, 246, 238)
INK = (24, 24, 24)
RED = (176, 30, 30)
RED_DK = (138, 18, 18)
BLUE = (28, 68, 128)
TEAL = (18, 108, 108)
GOLD = (198, 148, 38)
GREEN = (38, 118, 58)
PURPLE = (104, 74, 150)
GRAY = (118, 116, 110)
LIGHT = (236, 230, 218)
WHITE = (255, 255, 255)
SKY = (178, 210, 232)
NIGHT = (18, 28, 58)
SAND = (226, 206, 164)
SEA = (196, 222, 234)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            if fill:
                self.rect(cx - dx, yy, dx * 2 + 1, 1, c)
            else:
                self.set(cx - dx, yy, c)
                self.set(cx + dx, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, pts, c):
        # scanline fill for a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), y, int(xs[k + 1]) - int(xs[k]) + 1, 1, c)

    # -- text -------------------------------------------------------------
    def text_w(self, s, scale):
        return len(s) * 6 * scale

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, cx, y, s, scale, c):
        return self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        words = s.split(' ')
        lines, cur = [], ''
        for wd in words:
            t = wd if not cur else cur + ' ' + wd
            if self.text_w(t, scale) <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))

# -------------------------------------------------------------- content ----
# Every story below happened, or was first reported, on Sunday 22 Nov 2026.
HEROES = [
    dict(label="COP31: STILL NO DEAL", num="1", loc="ANTALYA, TURKIYE - CLIMATE",
         head="No deal as COP31 runs into day 14",
         body="Meant to close day 12. A third draft is late.",
         src="(ABC - Irish Times - RTE)", motif="cop31"),
    dict(label="BAHRAIN: IRAN STRIKES", num="2", loc="MANAMA, BAHRAIN - WAR",
         head="Iran hits two US bases in Bahrain",
         body="Drones hit two US bases; sirens sounded in Manama.",
         src="(Fars - UKMTO)", motif="bahrain"),
    dict(label="LAS VEGAS: F1 POLE", num="3", loc="LAS VEGAS, USA - FORMULA ONE",
         head="Verstappen on pole in Las Vegas",
         body="Race at 04:00 UTC. Antonelli fastest but penalised.",
         src="(Formula 1)", motif="f1"),
]

SECONDARY = [
    dict(tag="TRUMP", head="Trump: Iran deal 'could last 20 years'",
         src="(ToI)", motif="mic", bg=(222, 232, 244)),
    dict(tag="GAZA", head="Israel: Hamas tightening grip on Gaza",
         src="(01:02 UTC)", motif="flag", bg=(244, 224, 224)),
    dict(tag="AIRLINES", head="US airlines warned of terror threat",
         src="(ToI)", motif="plane", bg=(224, 240, 224)),
    dict(tag="KYIV", head="Zelensky calls Putin a 'murderer'",
         src="(japako)", motif="flag", bg=(240, 234, 200)),
    dict(tag="COPENHAGEN", head="Russia plotted to kill US-Ukrainian",
         src="(japako)", motif="flag", bg=(222, 232, 244)),
    dict(tag="SEOUL", head="S. Korea: $75,000 for exam-cheat tips",
         src="(japako)", motif="cash", bg=(240, 234, 200)),
    dict(tag="PATNA", head="Modi opens Nitish Setu over Ganges",
         src="(Jagran)", motif="bridge", bg=(224, 240, 224)),
    dict(tag="RANCHI", head="Cyclone Akvan grounds 14 flights",
         src="(Jagran)", motif="storm", bg=(244, 224, 224)),
    dict(tag="WELLINGTON", head="India face NZ in windy Wellington T20",
         src="(pw.live)", motif="ball", bg=(222, 232, 244)),
    dict(tag="LONDON", head="Prince William backs forest staff cover",
         src="(Jagran)", motif="crown", bg=(240, 234, 200)),
]

# (number, one-line item) -- 22 more stories, two columns of 11.
ALSO = [
    (14, "Tehran: Qeshm blasts were US ammo disposal (ToI)"),
    (15, "Washington: Trump shares 'TrumpCare' plan (ToI)"),
    (16, "Washington: FBI database breach raises alarm (bahjom)"),
    (17, "Khartoum: Sudan's home-grown push for peace (bahjom)"),
    (18, "Beirut: UNIFIL: south Lebanon still bears scars (japako)"),
    (19, "Jerusalem: Netanyahu rhetoric revives Rabin (bahjom)"),
    (20, "New Delhi: Air India extends Jeddah halt (Jagran)"),
    (21, "New Delhi: ICMR completes 100 tech transfers (Jagran)"),
    (22, "Sydney: Cummins keeps Cricket Australia backing (Jagran)"),
    (23, "Panaji: IFFI 2026 adds animation section (pw.live)"),
    (24, "Mumbai: Sensex falls; crude oil down 3% (pw.live)"),
    (25, "Antalya: COP31 AI pledge shunned by US tech (pw.live)"),
    (26, "Paris: France probes Depardieu over rape claim (ToI)"),
    (27, "Tel Aviv: Eisenkot invites Likud to talks (ToI)"),
    (28, "New Delhi: Pakistan minister to attend SCO talks (ToI)"),
    (29, "Manama: Bahrain probes Patriot interceptor crash (ToI)"),
    (30, "Hormuz: ADNOC vessel hit; one crew missing (pw.live)"),
    (31, "London: Miliband says EU deal not tied to fees (japako)"),
    (32, "Tel Aviv: Lieberman vows to oust Netanyahu (japako)"),
    (33, "Washington: $7.25bn Roundup deal approved (kkrow)"),
    (34, "Los Angeles: 1924 diner reopens as a nonprofit (ToI)"),
    (35, "Washington: FEMA staff sent home over bed bugs (ToI)"),
]

STATS = [
    ("DAY 14", "COP31, due to end day 12", 4),
    ("2", "US bases hit in Bahrain", 4),
    ("1", "tanker hit off Oman", 4),
    ("04:00", "UTC - Las Vegas GP starts", 4),
    ("$75,000", "S. Korea exam bounty", 3),
    ("14", "flights cut at Ranchi", 4),
]

REGIONS = [
    ("EUROPE 6", 6, BLUE), ("ASIA 8", 8, GOLD), ("MIDDLE EAST 10", 10, RED),
    ("", 1, GREEN), ("AMERICAS 8", 8, TEAL), ("OCEANIA 2", 2, PURPLE),
]

DATE_CHECK = ("Left out - they belong to Saturday 21 November: Peru's 6.7 quake - "
              "the Sparta II drone strike in the Baltic - 'El Chapo Isidro' captured, "
              "11 killed in Sinaloa - Bolsonaro taken to ICU - Estonia's border "
              "decision (20 Nov) - Australia beat England in the first T20 - "
              "BepiColombo's Mercury orbit insertion.")

# ----------------------------------------------------------- illustrations --
def draw_cop31(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + 70, y + 58, 38, BLUE)
    cv.circle(x + 55, y + 44, 12, GREEN)
    cv.circle(x + 86, y + 70, 10, GREEN)
    cv.circle(x + 68, y + 78, 8, GREEN)
    cv.rect(x + 152, y + 16, 14, 66, WHITE)
    cv.rect(x + 155, y + 40, 8, 42, RED)
    cv.circle(x + 159, y + 86, 11, RED)
    cv.circle(x + 262, y + 58, 30, WHITE)
    cv.circle(x + 262, y + 58, 30, INK, fill=False)
    cv.line(x + 262, y + 58, x + 262, y + 34, INK)
    cv.line(x + 262, y + 58, x + 278, y + 66, INK)
    cv.rect(x + 232, y + 8, 88, 20, RED)
    cv.text_c(x + 276, y + 13, "DAY 14", 2, WHITE)


def draw_bahrain(cv, x, y, w, h):
    cv.rect(x, y, w, h, NIGHT)
    for sx, sy in [(30, 14), (90, 10), (150, 18), (210, 8), (270, 16), (310, 24),
                   (60, 30), (120, 26), (190, 32), (250, 12)]:
        cv.set(x + sx, y + sy, WHITE)
        cv.set(x + sx + 1, y + sy, WHITE)
    # skyline
    for bx, bw, bh in [(0, 44, 46), (48, 36, 62), (88, 52, 40), (144, 40, 70),
                       (188, 48, 44), (240, 40, 58), (284, 44, 36)]:
        cv.rect(x + bx, y + h - bh, bw, bh, (8, 14, 30))
        for wy in range(y + h - bh + 8, y + h - 6, 12):
            for wx in range(x + bx + 6, x + bx + bw - 6, 12):
                cv.rect(wx, wy, 5, 6, GOLD)
    # drones with dashed paths
    for dx, dy in [(96, 30), (186, 22), (252, 40)]:
        cv.line(x + dx, y + dy + 14, x + dx + 26, y + dy + 34, GOLD)
        cv.circle(x + dx, y + dy, 4, WHITE)
        cv.line(x + dx - 7, y + dy, x + dx + 7, y + dy, WHITE)
    # explosion star over the skyline
    ex, ey = x + 252, y + 66
    for ang in range(0, 360, 30):
        import math
        r = 16
        cv.line(ex, ey, int(ex + r * math.cos(math.radians(ang))),
                int(ey + r * math.sin(math.radians(ang))), (255, 180, 60))
    cv.circle(ex, ey, 7, (255, 200, 80))


def draw_f1(cv, x, y, w, h):
    cv.rect(x, y, w, h, (26, 26, 34))
    # checkered flag
    for r in range(3):
        for c in range(4):
            col = WHITE if (r + c) % 2 == 0 else INK
            cv.rect(x + 268 + c * 8, y + 12 + r * 8, 8, 8, col)
    cv.rect(x + 266, y + 10, 36, 28, WHITE)  # placeholder border fix below
    for r in range(3):
        for c in range(4):
            col = WHITE if (r + c) % 2 == 0 else INK
            cv.rect(x + 268 + c * 8, y + 12 + r * 8, 8, 8, col)
    # speed lines
    for ly in (66, 76, 96):
        cv.line(x + 16, y + ly, x + 96, y + ly, GOLD)
    # track
    cv.rect(x, y + 92, w, 6, (70, 70, 78))
    cv.rect(x, y + 108, w, 2, WHITE)
    # race car
    cv.rect(x + 116, y + 66, 118, 16, RED)
    cv.rect(x + 158, y + 54, 34, 14, RED)
    cv.rect(x + 104, y + 76, 12, 8, WHITE)
    cv.rect(x + 228, y + 52, 8, 22, WHITE)
    for wx in (128, 196):
        cv.circle(x + wx, y + 86, 9, INK)
        cv.circle(x + wx, y + 86, 4, (150, 150, 150))
    cv.rect(x + 16, y + 12, 74, 20, GOLD)
    cv.text(x + 22, y + 17, "POLE", 2, INK)


def draw_motif(cv, x, y, w, h, kind, bg):
    cv.rect(x, y, w, h, bg)
    cx, cy = x + w // 2, y + h // 2
    if kind == "flag":
        cv.rect(cx - 2, y + 6, 3, h - 12, INK)
        cv.rect(cx, y + 6, 34, 18, RED)
        cv.rect(cx, y + 6, 14, 9, BLUE)
    elif kind == "plane":
        cv.rect(cx - 34, cy - 4, 68, 10, INK)
        cv.rect(cx - 8, cy - 14, 22, 8, INK)
        cv.rect(cx + 18, cy - 10, 6, 20, INK)
    elif kind == "cash":
        cv.rect(cx - 36, cy - 12, 72, 24, GREEN)
        cv.rect(cx - 30, cy - 8, 60, 16, WHITE)
        cv.text_c(cx, cy - 7, "$", 2, GREEN)
    elif kind == "bridge":
        cv.line(x + 8, y + h - 8, cx, y + 8, RED)
        cv.line(cx, y + 8, x + w - 8, y + h - 8, RED)
        cv.rect(x + 8, y + h - 12, w - 16, 4, INK)
    elif kind == "storm":
        cv.circle(cx - 12, cy - 4, 12, (90, 90, 96))
        cv.circle(cx + 10, cy - 4, 12, (90, 90, 96))
        for rx in (-18, -6, 6, 18):
            cv.line(cx + rx, cy + 12, cx + rx - 4, cy + 18, BLUE)
    elif kind == "ball":
        cv.circle(cx, cy, 15, WHITE)
        cv.circle(cx, cy, 15, INK, fill=False)
        cv.line(cx - 15, cy, cx + 15, cy, INK)
        cv.line(cx, cy - 15, cx, cy + 15, INK)
    elif kind == "crown":
        cv.poly([(cx - 30, cy + 12), (cx - 30, cy - 8), (cx - 15, cy + 2),
                 (cx, cy - 12), (cx + 15, cy + 2), (cx + 30, cy - 8),
                 (cx + 30, cy + 12)], GOLD)
    elif kind == "mic":
        cv.circle(cx, cy - 8, 11, INK)
        cv.rect(cx - 2, cy + 4, 4, 12, INK)
        cv.rect(cx - 12, cy + 16, 24, 3, INK)
    else:
        cv.circle(cx, cy, 14, BLUE)
        cv.circle(cx - 5, cy - 5, 5, GREEN)
        cv.circle(cx + 6, cy + 5, 4, GREEN)


# ---------------------------------------------------------------- layout ---
def box(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 1, INK)
    cv.rect(x, y + h - 1, w, 1, INK)
    cv.rect(x, y, 1, h, INK)
    cv.rect(x + w - 1, y, 1, h, INK)


def compose():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 30, RED)
    cv.text(12, 8, "THE WORLD IN ONE DAY", 2, WHITE)
    cv.text(1012 - cv.text_w("35 STORIES - 6 REGIONS", 2), 8,
            "35 STORIES - 6 REGIONS", 2, WHITE)
    # date headline
    cv.text_c(512, 36, "Sunday 22 November 2026", 6, INK)
    cv.text_c(512, 84,
              "COP31 still no deal - Iran hits US bases - F1 under lights",
              2, INK)
    cv.rect(10, 106, 1004, 2, INK)
    # stat strip
    for i, (num, lab, sc) in enumerate(STATS):
        bx = i * 172
        cv.rect(bx, 112, 164, 54, LIGHT)
        cv.rect(bx, 112, 3, 54, RED)
        cv.text_c(bx + 82, 118, num, sc, RED_DK)
        for j, ln in enumerate(cv.wrap(lab, 148, 1)):
            cv.text_c(bx + 82, 148 + j * 8, ln, 1, INK)
    # region bar
    total = sum(c for _, c, _ in REGIONS)
    rx = 10
    for label, count, col in REGIONS:
        rw = int(1004 * count / total)
        cv.rect(rx, 170, rw, 20, col)
        if label and rw >= 60:
            cv.text_c(rx + rw // 2, 175, label, 1, WHITE)
        rx += rw
    # hero row
    hy = 194
    for i, st in enumerate(HEROES):
        hx = 10 + i * 338
        box(cv, hx, hy, 328, 274)
        draw = {"cop31": draw_cop31, "bahrain": draw_bahrain,
                "f1": draw_f1}[st["motif"]]
        draw(cv, hx + 1, hy + 1, 326, 120)
        cv.rect(hx + 1, hy + 121, 326, 24, RED)
        cv.text(hx + 9, hy + 126, st["label"], 2, WHITE)
        cv.circle(hx + 17, hy + 155, 8, RED)
        cv.text_c(hx + 17, hy + 152, st["num"], 1, WHITE)
        cv.text(hx + 32, hy + 152, st["loc"], 1, RED_DK)
        for j, ln in enumerate(cv.wrap(st["head"], 312, 3)[:2]):
            cv.text(hx + 9, hy + 168 + j * 22, ln, 3, INK)
        for j, ln in enumerate(cv.wrap(st["body"], 312, 2)[:3]):
            cv.text(hx + 9, hy + 216 + j * 14, ln, 2, INK)
        cv.text(hx + 328 - 9 - cv.text_w(st["src"], 1), hy + 260,
                st["src"], 1, GRAY)
    # secondary rows
    for row in range(2):
        sy = 474 + row * 156
        for col in range(5):
            st = SECONDARY[row * 5 + col]
            sx = 2 + col * 206
            box(cv, sx, sy, 196, 150)
            draw_motif(cv, sx + 1, sy + 1, 194, 44, st["motif"], st["bg"])
            cv.rect(sx + 1, sy + 45, 194, 18, RED)
            cv.text(sx + 9, sy + 49, st["tag"], 2, WHITE)
            for j, ln in enumerate(cv.wrap(st["head"], 182, 2)[:4]):
                cv.text(sx + 8, sy + 69 + j * 14, ln, 2, INK)
            cv.text(sx + 196 - 9 - cv.text_w(st["src"], 1), sy + 134,
                    st["src"], 1, GRAY)
    # map + also list
    my = 786
    cv.text(10, my + 4, "WHERE IT HAPPENED", 2, INK)
    cv.text(320, my + 4, "ALSO ON SUNDAY 22 NOVEMBER - 22 MORE STORIES", 2, INK)
    cv.rect(10, my + 22, 300, 104, SEA)
    mx, myy = 10, my + 22

    def shifted(pts):
        return [(mx + px, myy + py) for px, py in pts]

    cv.poly(shifted([(18, 18), (64, 10), (104, 16), (100, 38), (78, 52),
                     (56, 46), (28, 42), (14, 28)]), SAND)
    cv.poly(shifted([(72, 58), (92, 56), (102, 68), (92, 92), (78, 88)]),
            SAND)
    cv.poly(shifted([(138, 14), (162, 9), (172, 24), (158, 34), (142, 28)]),
            SAND)
    cv.poly(shifted([(138, 44), (168, 41), (178, 58), (164, 82), (148, 78),
                     (138, 58)]), SAND)
    cv.poly(shifted([(178, 11), (248, 9), (278, 24), (268, 44), (238, 48),
                     (208, 44), (182, 34)]), SAND)
    cv.poly(shifted([(248, 74), (272, 71), (280, 84), (258, 88)]), SAND)
    pins = [(1, 168, 26), (2, 200, 40), (3, 34, 34), (4, 52, 30),
            (5, 182, 36), (6, 60, 38), (7, 158, 22), (8, 150, 16),
            (9, 252, 26), (10, 222, 38), (11, 232, 46), (12, 282, 90),
            (13, 146, 18)]
    for n, px, py in pins:
        cv.circle(10 + px, my + 22 + py, 6, RED)
        cv.text_c(10 + px, my + 22 + py - 3, str(n), 1, WHITE)
    for k, (n, item) in enumerate(ALSO):
        col = 0 if k < 11 else 1
        ix = 320 + col * 355
        iy = my + 24 + (k % 11) * 9
        cv.text(ix, iy, "%d %s" % (n, item), 1, INK)
    # date check
    dy = 920
    cv.rect(10, dy, 1004, 64, PAPER)
    cv.rect(10, dy, 1004, 2, RED)
    cv.rect(10, dy + 62, 1004, 2, RED)
    cv.rect(10, dy, 2, 64, RED)
    cv.rect(1012, dy, 2, 64, RED)
    cv.text(18, dy + 7, "DATE CHECK", 2, RED_DK)
    for j, ln in enumerate(cv.wrap(DATE_CHECK, 980, 1)[:2]):
        cv.text(18, dy + 26 + j * 9, ln, 1, INK)
    # footer
    cv.text_c(512, 996,
              "Every story here happened, or was first reported, on Sunday "
              "22 November 2026. Sources named beside each story - "
              "Original drawings", 1, GRAY)
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    data = png_bytes(compose())
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
