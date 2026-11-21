# Passport spread of the Republic of Kaldera — a country that isn't there.
# Renders one 1024x1024 image to $MAKEFUN_OUTPUT_DIR/entry.png with Pillow only.

import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

random.seed(20261121)

SC = 2  # supersample factor; every coordinate below is in final 1024-space * SC

# ---------------------------------------------------------------- fonts ----

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def vendored(name):
    return os.path.join(FONT_DIR, name)


SERIF_BOLD = [
    vendored("SourceSerifPro-Semibold.ttf"),
    vendored("SourceSerifPro-Bold.ttf"),
    vendored("DejaVuSerif-Bold.ttf"),
]
SERIF_BLACK = [
    vendored("SourceSerifPro-Black.ttf"),
    vendored("SourceSerifPro-Bold.ttf"),
    vendored("DejaVuSerif-Bold.ttf"),
]
SANS = [
    vendored("SourceSansPro-Regular.ttf"),
    vendored("DejaVuSans.ttf"),
]
SANS_SEMI = [
    vendored("SourceSansPro-Semibold.ttf"),
    vendored("SourceSansPro-Bold.ttf"),
    vendored("DejaVuSans-Bold.ttf"),
]
MONO = [
    vendored("DejaVuSansMono.ttf"),
]
SCRIPT = [
    vendored("Niconne-Regular.ttf"),
    vendored("SourceSerifPro-Semibold.ttf"),
]


def load_font(cands, size):
    for path in cands:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def font_ascent(font):
    try:
        return font.getmetrics()[0]
    except Exception:
        pass
    try:
        return font.size
    except Exception:
        return int(size_guess(font))


def size_guess(font):
    try:
        box = font.getbbox("Ag")
        return max(1, box[3] - box[1])
    except Exception:
        return 11


# ------------------------------------------------------------- helpers ----

def tracked(draw, xy, text, font, fill, track=0, center=True):
    """Letter-spaced text. Returns total width."""
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x = xy[0] - total / 2 if center else xy[0]
    for c, w in zip(text, widths):
        draw.text((x, xy[1]), c, font=font, fill=fill)
        x += w + track
    return total


def tracked_width(draw, text, font, track=0):
    widths = [draw.textlength(c, font=font) for c in text]
    return sum(widths) + track * (len(text) - 1)


def rrect(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


# ---------------------------------------------------------- check digits --

def mrz_cd(s):
    weights = [7, 3, 1]
    v = 0
    for i, c in enumerate(s):
        if c == "<":
            n = 0
        elif c.isdigit():
            n = int(c)
        else:
            n = ord(c) - 55
        v += n * weights[i % 3]
    return str(v % 10)


# ------------------------------------------------------------- palette ----

INK = (30, 34, 33)          # document printing ink
LABEL = (108, 104, 92)      # field label gray
PAPER = (243, 240, 231)
DESK = (38, 47, 42)
EMBLEM = (26, 62, 64)       # deep teal

STAMP_TEAL = (18, 96, 100)
STAMP_INDIGO = (48, 58, 128)
STAMP_RED = (152, 44, 48)
STAMP_OCHRE = (148, 104, 40)


# ------------------------------------------------------------- portrait ---

def portrait_shade(w, h):
    """Grayscale shading map of a bust portrait (255 = paper, low = ink)."""
    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    cx = w * 0.5
    k = w / 300.0  # design basis is 300 wide

    def E(x0, y0, x1, y1, **kw):
        d.ellipse([x0 * k, y0 * k, x1 * k, y1 * k], **kw)

    # neck + head base
    d.rectangle([(cx - 30) * k, 280 * k, (cx + 30) * k, 400 * k], fill=178)
    E(105, 262, 195, 330, fill=196)
    E(58, 62, 242, 300, fill=214)  # face
    # shading: jaw / sides
    d.ellipse([55 * k, 150 * k, 120 * k, 305 * k], fill=198)
    d.ellipse([180 * k, 150 * k, 245 * k, 305 * k], fill=198)
    # cheeks soft
    E(88, 216, 138, 268, fill=204)
    E(162, 216, 212, 268, fill=204)
    # hair: rim behind face
    E(50, 46, 250, 292, fill=52)
    E(64, 68, 236, 262, fill=214)  # face again, leaves hair rim
    # long side hair
    d.rounded_rectangle([48 * k, 130 * k, 86 * k, 330 * k], radius=18 * k, fill=56)
    d.rounded_rectangle([214 * k, 130 * k, 252 * k, 330 * k], radius=18 * k, fill=56)
    # part line
    d.line([(150 * k, 74 * k), (150 * k, 120 * k)], fill=70, width=max(1, int(2 * k)))
    # ears
    E(54, 180, 74, 216, fill=198)
    E(226, 180, 246, 216, fill=198)
    # brows
    d.arc([94 * k, 148 * k, 140 * k, 176 * k], 200, 340, fill=72, width=max(1, int(5 * k)))
    d.arc([160 * k, 148 * k, 206 * k, 176 * k], 200, 340, fill=72, width=max(1, int(5 * k)))
    # eyes
    for ex in (98, 164):
        E(ex, 182, ex + 38, 198, fill=246)
        E(ex + 12, 184, ex + 26, 196, fill=64)
        E(ex + 17, 187, ex + 21, 191, fill=24)
        d.arc([ex * k, 182 * k, (ex + 38) * k, 200 * k], 190, 350, fill=70,
              width=max(1, int(3 * k)))
    # nose shadow
    d.polygon([(158 * k, 180 * k), (166 * k, 238 * k), (150 * k, 246 * k)], fill=158)
    E(138, 240, 148, 248, fill=96)
    E(152, 240, 162, 248, fill=96)
    E(142, 226, 158, 244, fill=176)
    # mouth
    d.arc([130 * k, 250 * k, 170 * k, 272 * k], 20, 160, fill=92, width=max(1, int(4 * k)))
    E(136, 260, 164, 280, fill=188)
    E(133, 266, 141, 274, fill=112)
    E(159, 266, 167, 274, fill=112)
    # chin shadow
    E(134, 284, 166, 300, fill=196)
    # shoulders / coat over the neck
    d.polygon([(10 * k, 400 * k), (10 * k, 352 * k), (70 * k, 336 * k),
               (122 * k, 362 * k), (150 * k, 344 * k), (178 * k, 362 * k),
               (230 * k, 336 * k), (290 * k, 352 * k), (290 * k, 400 * k)],
              fill=58)
    d.polygon([(126 * k, 400 * k), (150 * k, 350 * k), (174 * k, 400 * k)],
              fill=236)
    d.line([(150 * k, 350 * k), (118 * k, 400 * k)], fill=40, width=max(1, int(4 * k)))
    d.line([(150 * k, 350 * k), (182 * k, 400 * k)], fill=40, width=max(1, int(4 * k)))

    img = img.filter(ImageFilter.GaussianBlur(2.2 * k / 2))
    img = ImageEnhance.Contrast(img).enhance(1.35)
    return img


def engrave(shade, gap=4):
    """Convert a shading map into horizontal engraving lines (L image)."""
    w, h = shade.size
    # deepen mid tones so lines read at small sizes
    shade = shade.point(lambda v: max(0, 255 - int((255 - v) * 1.7)))
    px = shade.load()
    out = Image.new("L", (w, h), 255)
    od = out.load()
    for y in range(0, h, gap):
        for x in range(w):
            v = px[x, y]
            if v >= 250:
                continue
            t = (255 - v) / 255.0 * (gap - 1.2)
            t += math.sin(x * 0.11 + y * 1.9) * 0.22
            if t > 0.3:
                od[x, y] = max(0, int(255 - min(255.0, t * 120)))
    return out


def make_portrait(box_w, box_h):
    """RGBA portrait with transparent background, dark ink lines."""
    shade = portrait_shade(box_w, box_h)
    lines = engrave(shade)
    inv = lines.point(lambda v: 255 - v)  # mask: ink where dark
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    ink = Image.new("RGBA", (box_w, box_h), (38, 40, 42, 255))
    img.paste(ink, (0, 0), inv)
    return img


# --------------------------------------------------------- document art ---

def rosette(draw, cx, cy, r, color, petals=9, turns=42):
    pts = []
    n = turns * 24
    for i in range(n + 1):
        t = i / n * 2 * math.pi * petals
        rr = r * (0.55 + 0.45 * math.sin(t * 0.5 + 1.2))
        a = i / n * 2 * math.pi * turns / petals * petals
        x = cx + rr * math.cos(a)
        y = cy + rr * math.sin(a)
        pts.append((x, y))
    draw.line(pts, fill=color, width=1)


def wave_lines(draw, x0, x1, y0, y1, color, step=13, amp=7):
    y = y0
    phase = 0.0
    while y < y1:
        pts = []
        for x in range(x0, x1 + 1, 8):
            pts.append((x, y + amp * math.sin(x * 0.02 + phase)))
        draw.line(pts, fill=color, width=1)
        phase += 0.55
        y += step


def draw_emblem(layer, cx, cy, r, color, width_scale=1.0):
    d = ImageDraw.Draw(layer)
    lw = max(1, int(5 * width_scale))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=lw)
    r2 = r - 13 * width_scale
    d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=color,
              width=max(1, int(2 * width_scale)))
    # volcano
    vr = r2 * 0.62
    d.polygon([(cx - vr, cy + vr * 0.55), (cx, cy - vr * 0.75), (cx + vr, cy + vr * 0.55)],
              outline=color, width=max(1, int(4 * width_scale)))
    # snow / crater notch
    d.polygon([(cx - vr * 0.28, cy - vr * 0.44), (cx, cy - vr * 0.75),
               (cx + vr * 0.28, cy - vr * 0.44)], fill=color)
    # twin tides: three wave arcs under the volcano
    for i in range(3):
        yy = cy + vr * 0.62 + i * 14 * width_scale
        half = vr * (0.95 - i * 0.08)
        d.arc([cx - half, yy - 10 * width_scale, cx + half, yy + 10 * width_scale],
              200, 340, fill=color, width=max(1, int(4 * width_scale)))
    # star above
    sr = r * 0.16
    sy = cy - r2 * 0.72
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = sr if i % 2 == 0 else sr * 0.45
        pts.append((cx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


# ------------------------------------------------------------- stamps ----

def arc_text(layer, cx, cy, r, text, font, fill, top=True):
    d = ImageDraw.Draw(layer)
    widths = [d.textlength(c, font=font) for c in text]
    spans = [w / r for w in widths]
    dirn = 1 if top else -1
    a0 = (-math.pi / 2 if top else math.pi / 2) - dirn * sum(spans) / 2
    a = a0
    try:
        ascent, descent = font.getmetrics()
        ch = ascent + descent
    except Exception:
        ch = int(2.2 * size_guess(font))
    for i, (c, sp) in enumerate(zip(text, spans)):
        ang = a + (sp / 2) * dirn
        px = cx + r * math.cos(ang)
        py = cy + r * math.sin(ang)
        gw = int(widths[i]) + 12
        gh = ch + 12
        glyph = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((6, 4), c, font=font, fill=fill)
        rot = math.degrees(ang) + (90 if top else -90)
        glyph = glyph.rotate(rot, expand=True, resample=Image.BICUBIC)
        layer.alpha_composite(glyph, (int(px - glyph.width / 2), int(py - glyph.height / 2)))
        a += sp * dirn


def inkify(layer, opacity):
    """Give a flat stamp layer mottled ink texture, return composited RGBA."""
    noise = Image.effect_noise(layer.size, 46).point(lambda v: int(120 + v * 0.53))
    a = layer.getchannel("A")
    a = ImageChops.multiply(a, noise)
    a = a.filter(ImageFilter.GaussianBlur(0.7))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    solid = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    solid.paste(layer, (0, 0))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    rgb = layer.copy()
    rgb.putalpha(a)
    out.alpha_composite(rgb)
    if opacity < 1.0:
        alphas = out.getchannel("A").point(lambda v: int(v * opacity))
        out.putalpha(alphas)
    return out


def oval_stamp(size, color, top, bottom, midlines, small=None):
    w, h = int(size[0]), int(size[1])
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = w / 2, h / 2
    rx, ry = w / 2 - 6, h / 2 - 6
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=color, width=6)
    r2x, r2y = rx - 14, ry - 14
    d.ellipse([cx - r2x, cy - r2y, cx + r2x, cy + r2y], outline=color, width=3)
    f_mid = load_font(SANS_SEMI, 44)
    f_arc = load_font(SANS_SEMI, 30)
    f_small = load_font(SANS, 26)
    arc_text(layer, cx, cy, ry - 34, top, f_arc, color, top=True)
    if bottom:
        arc_text(layer, cx, cy, ry - 30, bottom, f_arc, color, top=False)
    y = cy - (len(midlines) - 1) * 30
    for i, ln in enumerate(midlines):
        f = f_mid if i == 0 else (f_small if small else f_mid)
        tw = d.textlength(ln, font=f)
        d.text((cx - tw / 2, y - font_ascent(f) // 2), ln, font=f, fill=color)
        y += 58 if f is f_mid else 40
    return layer


def rect_stamp(size, color, header, rows, footer=None):
    w, h = int(size[0]), int(size[1])
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rrect(d, [4, 4, w - 4, h - 4], radius=14, outline=color, width=6)
    rrect(d, [16, 16, w - 16, h - 16], radius=9, outline=color, width=3)
    f_h = load_font(SANS_SEMI, 32)
    f_r = load_font(SANS, 27)
    f_f = load_font(SANS_SEMI, 30)
    y = 34
    tw = d.textlength(header, font=f_h)
    d.text(((w - tw) / 2, y), header, font=f_h, fill=color)
    y += 48
    d.line([(26, y), (w - 26, y)], fill=color, width=2)
    y += 14
    for row in rows:
        tw = d.textlength(row, font=f_r)
        d.text(((w - tw) / 2, y), row, font=f_r, fill=color)
        y += 38
    if footer:
        tw = d.textlength(footer, font=f_f)
        d.text(((w - tw) / 2, h - 52), footer, font=f_f, fill=color)
    return layer


def place_stamp(canvas, layer, center, angle, opacity=0.86):
    layer = inkify(layer, opacity)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(layer, (int(center[0] - layer.width / 2),
                                   int(center[1] - layer.height / 2)))


# ------------------------------------------------------------ MRZ ---------

def build_mrz():
    pno = "K0284171<"
    nat = "KLD"
    dob = "850412"
    sex = "F"
    exp = "330410"
    name = "VELLANDA<<MIRA<ASKA"
    per = "<" * 14
    c1 = mrz_cd(pno)
    c2 = mrz_cd(dob)
    c3 = mrz_cd(exp)
    c4 = mrz_cd(per)
    comp = mrz_cd(pno + c1 + dob + c2 + exp + c3 + per + c4)
    l1 = ("P<" + nat + name)
    l1 = l1 + "<" * (44 - len(l1))
    l2 = pno + c1 + nat + dob + c2 + sex + exp + c3 + per + c4 + comp
    assert len(l1) == 44 and len(l2) == 44
    return l1, l2


# ------------------------------------------------------------ layout ------

def paper_page(w, h):
    page = Image.new("RGB", (w, h), PAPER)
    # subtle vertical tone
    grad = Image.new("L", (1, h))
    for y in range(h):
        grad.putpixel((0, y), int(10 * math.sin(y / h * math.pi)))
    grad = grad.resize((w, h))
    page = ImageChops.subtract(page, Image.merge("RGB", (grad, grad, grad)))
    # speckle
    noise = Image.effect_noise((w, h), 13)
    page = ImageChops.subtract(page, Image.merge("RGB", (noise, noise, noise)).point(
        lambda v: v // 22))
    return page.convert("RGBA")


def shade_spine(page, side):
    """Darken the edge nearest the spine. side='right' for left page."""
    w, h = page.size
    band_w = int(w * 0.16)
    grad = Image.new("L", (w, 1), 0)
    for x in range(band_w):
        t = 1 - x / band_w
        val = int(26 * (t ** 1.6))
        if side == "right":
            grad.putpixel((x, 0), val)
        else:
            grad.putpixel((w - 1 - x, 0), val)
    grad = grad.resize((w, h))
    dark = Image.merge("RGB", (grad, grad, grad))
    rgb = page.convert("RGB")
    page = ImageChops.subtract(rgb, dark)
    return page.convert("RGBA")


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    rrect(d, [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def tri(d, cx, cy, s, fill):
    d.polygon([(cx - s, cy - s * 0.9), (cx + s, cy), (cx - s, cy + s * 0.9)], fill=fill)


# ------------------------------------------------------------- main -------

def radial_gradient(size=256):
    """L image: 0 at centre, 255 at corners (manual, Pillow-version safe)."""
    g = Image.new("L", (size, size))
    px = g.load()
    c = (size - 1) / 2.0
    maxr = math.hypot(c, c)
    for y in range(size):
        dy = y - c
        for x in range(size):
            px[x, y] = int(math.hypot(x - c, dy) / maxr * 255 + 0.5)
    return g


def render():
    W = H = 1024 * SC
    canvas = Image.new("RGBA", (W, H), DESK + (255,))
    base = canvas.convert("RGB")

    # desk noise + gentle vignette (alpha overlay, never clipped to black)
    noise = Image.effect_noise((W, H), 16)
    base = ImageChops.subtract(base, Image.merge("RGB", (noise, noise, noise)).point(
        lambda v: v // 20))
    vig = radial_gradient().resize((W, H)).point(lambda v: int(v * 0.22))
    vig_overlay = Image.merge("RGBA", (
        Image.new("L", (W, H), 0),
        Image.new("L", (W, H), 0),
        Image.new("L", (W, H), 0),
        vig,
    ))
    base = Image.alpha_composite(base.convert("RGBA"), vig_overlay)
    canvas = base

    # ----- shadow under the spread
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    rrect(ds, [70, 118, W - 70, 1968], radius=30, fill=(0, 0, 0, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    canvas.alpha_composite(sh)

    # ----- page geometry (2x space)
    PW, PH = 908, 1792
    PY = 128
    LX0, RX0 = 84, 1056

    def build_page(side):
        page = paper_page(PW, PH)
        page = shade_spine(page, side)
        return page

    left = build_page("right")
    right = build_page("left")

    dl = ImageDraw.Draw(left)
    dr = ImageDraw.Draw(right)

    # ============================ LEFT PAGE (data page) ===================
    lcx = PW // 2
    mx = 64

    # guilloche rosette behind emblem
    rosette(dl, lcx, 232, 96, (196, 194, 182))
    draw_emblem(left, lcx, 232, 92, EMBLEM)

    f_name = load_font(SERIF_BOLD, 52)
    tracked(dl, (lcx, 372), "REPUBLIC OF KALDERA", f_name, INK, track=3)
    f_sub = load_font(SANS_SEMI, 22)
    tracked(dl, (lcx, 452), "ORDINARY PASSPORT · VEIGBÓK", f_sub, (96, 92, 82), track=6)
    dl.line([(mx, 508), (PW - mx, 508)], fill=(120, 116, 102), width=2)
    dl.line([(mx, 514), (PW - mx, 514)], fill=(120, 116, 102), width=1)

    # ghost portrait (large, faint)
    ghost = make_portrait(300, 400).resize((330, 440), Image.LANCZOS)
    gmask = ghost.getchannel("A").point(lambda v: v // 4)
    left.paste(Image.new("RGBA", ghost.size, (118, 116, 104, 255)), (560, 580), gmask)

    # photo box
    phx, phy, phw, phh = 92, 596, 240, 316
    rrect(dl, [phx - 3, phy - 3, phx + phw + 3, phy + phh + 3], radius=8,
          fill=(226, 223, 214), outline=(148, 145, 134), width=2)
    port = make_portrait(phw, phh)
    left.paste(port, (phx, phy), port)

    # fields
    f_label = load_font(SANS_SEMI, 17)
    f_val = load_font(SANS, 26)
    f_val_big = load_font(SANS_SEMI, 34)

    def field(d, x, y, en, kal, value, big=False, w=None):
        label = en + " · " + kal if kal else en
        tracked(d, (x, y), label, f_label, LABEL, track=1, center=False)
        f = f_val_big if big else f_val
        d.text((x, y + 24), value, font=f, fill=INK)

    fx = 372
    field(dl, fx, 596, "TYPE", "GERD", "P")
    field(dl, fx + 130, 596, "CODE", "KODI", "KLD")
    field(dl, fx, 668, "PASSPORT NO.", "RAÐNÍMERKI", "K0284171", big=True)
    field(dl, fx, 760, "NATIONALITY", "ÞJÓÐFÉLAG", "KALDERAN")

    field(dl, 92, 962, "SURNAME", "STAMNAVN", "VELLANDA", big=True)
    field(dl, 92, 1056, "GIVEN NAMES", "FORNANVN", "MIRA ASKA", big=True)

    field(dl, 92, 1168, "DATE OF BIRTH", "FØÐINGARDAGUR", "12 APR 1985")
    field(dl, 700, 1168, "SEX", "KYN", "F")

    field(dl, 92, 1248, "PLACE OF BIRTH", "FØÐSTAÐUR", "BRAYSTONE")

    field(dl, 92, 1328, "DATE OF ISSUE", "ÚTGÁFUDAGUR", "11 APR 2023")
    field(dl, 560, 1328, "DATE OF EXPIRY", "GILDISTÍMI", "10 APR 2033")

    field(dl, 92, 1408, "AUTHORITY", "ÚTGEFANDI",
          "MINISTRY OF TIDES AND RECORDS, PORT VEYRA")

    # signature
    sig_f = load_font(SCRIPT, 58)
    dl.text((120, 1486), "Mira A. Vellanda", font=sig_f, fill=(38, 48, 96))
    dl.line([(92, 1572), (520, 1572)], fill=(90, 88, 80), width=2)
    tracked(dl, (92, 1584), "SIGNATURE OF BEARER · MEÐFÆRANDA", f_label, LABEL,
            track=1, center=False)
    field(dl, 620, 1486, "DOCUMENT No.", "", "K0284171")

    # MRZ strip
    l1, l2 = build_mrz()
    f_mrz = load_font(MONO, 27)
    bx0, by0, bx1, by1 = mx - 6, 1620, PW - mx + 6, 1760
    rrect(dl, [bx0, by0, bx1, by1], radius=10, fill=(250, 249, 245),
          outline=(190, 187, 176), width=2)
    # MRZ corner markers
    tri(dl, bx0 + 26, by0 + 16, 9, (60, 60, 58))
    tri(dl, bx0 + 48, by0 + 16, 9, (60, 60, 58))
    tri(dl, bx1 - 26, by0 + 16, 9, (60, 60, 58))
    tri(dl, bx1 - 48, by0 + 16, 9, (60, 60, 58))
    dl.text((lcx - dl.textlength(l1, font=f_mrz) / 2, by0 + 40), l1,
            font=f_mrz, fill=(25, 25, 25))
    dl.text((lcx - dl.textlength(l2, font=f_mrz) / 2, by0 + 78), l2,
            font=f_mrz, fill=(25, 25, 25))

    # perforated number down the inner edge
    f_perf = load_font(SANS_SEMI, 40)
    for i, c in enumerate("K0284171"):
        y = 610 + i * 136
        dl.text((PW - 104 + 3, y + 3), c, font=f_perf, fill=(16, 24, 20))
        dl.text((PW - 104, y), c, font=f_perf, fill=(30, 38, 34))

    # page number
    dl.text((40, PH - 60), "4", font=load_font(SANS, 24), fill=(110, 106, 94))

    # ============================ RIGHT PAGE (visas) ======================
    rcx = PW // 2

    wave_lines(dr, 40, PW - 40, 210, 1560, (188, 190, 186), step=12, amp=6)
    rosette(dr, 300, 1240, 130, (200, 200, 194))
    draw_emblem(right, 300, 1240, 108, (206, 205, 196))
    # recolor emblem watermark faintly: draw already faint color; ok

    f_head = load_font(SERIF_BOLD, 34)
    tracked(dr, (rcx, 150), "LANDFALLS AND VISAS", f_head, INK, track=5)
    dr.line([(mx, 216), (PW - mx, 216)], fill=(120, 116, 102), width=2)
    dr.line([(mx, 222), (PW - mx, 222)], fill=(120, 116, 102), width=1)

    f_note = load_font(SANS, 19)
    note1 = "This passport remains the property of the Ministry of Tides and Records."
    note2 = "It is forfeit if carried beyond the reef line without sanction."
    dr.text(((PW - dr.textlength(note1, font=f_note)) / 2, PH - 116), note1,
            font=f_note, fill=(96, 92, 84))
    dr.text(((PW - dr.textlength(note2, font=f_note)) / 2, PH - 86), note2,
            font=f_note, fill=(96, 92, 84))
    dr.text((PW - 52, PH - 60), "5", font=load_font(SANS, 24), fill=(110, 106, 94))

    # stamps
    a = oval_stamp((300, 190), STAMP_INDIGO,
                   "OSTRAVEL BORDER POLICE", "OSTRHAVN AIRPORT",
                   ["ARRIVED", "14 JUN 2023"])
    place_stamp(right, a, (270, 400), -7)

    b = oval_stamp((300, 190), STAMP_TEAL,
                   "OSTRAVEL BORDER POLICE", "OSTRHAVN AIRPORT",
                   ["DEPARTED", "28 JUN 2023"])
    place_stamp(right, b, (640, 470), 5)

    c = rect_stamp((430, 268), STAMP_TEAL,
                   "BORDER SERVICE OF KALDERA",
                   ["PORT VEYRA · OUTER HARBOUR",
                    "LANDFALL PERMIT — MV GREBE SOUND",
                    "CREW ONLY · SHORE LEAVE ENDS AT DUSK",
                    "HARBOUR LEVY PAID — KRD 12 · REF T-24-118"],
                   footer="02 JUL 2023")
    place_stamp(right, c, (452, 760), -3)

    d_ = rect_stamp((360, 200), STAMP_RED,
                    "MERIDIAN REPUBLIC — CONSULATE",
                    ["VISA FEE 60 MRK PAID",
                     "SINGLE ENTRY · 30 DAYS"],
                    footer="12 SEP 2024")
    place_stamp(right, d_, (250, 1130), -6)

    e = oval_stamp((300, 190), STAMP_INDIGO,
                   "MERIDIAN REPUBLIC", "GREBE CROSSING (LAND)",
                   ["ENTRY", "20 SEP 2024"])
    place_stamp(right, e, (630, 1180), 6)

    f_ = rect_stamp((380, 178), STAMP_OCHRE,
                    "MERIDIAN REPUBLIC",
                    ["DEPARTURE · GREBE CROSSING",
                     "BY ROAD · 05 OCT 2024"])
    place_stamp(right, f_, (460, 1440), 2)

    # ----- paste pages onto canvas with rounded corners
    rad = 14 * SC
    for page, x0 in ((left, LX0), (right, RX0)):
        mask = rounded_mask(page.size, rad)
        canvas.paste(page, (x0, PY), mask)

    # spine shading between pages
    sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dsp = ImageDraw.Draw(sp)
    gx = (RX0 + LX0 + PW) // 2
    for i in range(26):
        a = int(80 * (1 - i / 26))
        dsp.line([(gx - i, PY + 6), (gx - i, PY + PH - 6)], fill=(0, 0, 0, a))
        dsp.line([(gx + i, PY + 6), (gx + i, PY + PH - 6)], fill=(0, 0, 0, a))
    canvas.alpha_composite(sp)

    # slight warm light across the spread from top-left
    glow = radial_gradient()
    glow = Image.eval(glow, lambda v: 255 - v)
    glow = glow.resize((W, H)).point(lambda v: int(v * 0.06))
    canvas = Image.alpha_composite(
        canvas,
        Image.merge("RGBA", [
            Image.new("L", (W, H), 255),
            Image.new("L", (W, H), 252),
            Image.new("L", (W, H), 240),
            glow,
        ]),
    )

    return canvas.convert("RGB")


def main():
    img = render()
    final = img.resize((1024, 1024), Image.LANCZOS)
    os.makedirs(OUT_DIR, exist_ok=True)
    final.save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    if size > 1048576:
        final.save(OUT_PATH, "JPEG", quality=92, optimize=True)
    print("wrote", OUT_PATH, os.path.getsize(OUT_PATH), "bytes")


if __name__ == "__main__":
    main()
