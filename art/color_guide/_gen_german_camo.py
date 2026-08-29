# one-shot generator for german_camo_colors.png
# wartime reconstructions for AFV painting; not modern RAL chips

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "german_camo_colors.png")

W, H = 2480, 4200
BG = (18, 16, 14)
INK = (236, 228, 214)
INK_DIM = (168, 158, 142)
INK_MUTED = (120, 112, 100)
RULE = (58, 52, 44)
ACCENT = (196, 168, 96)

FONT_DIR = "/System/Library/Fonts/Supplemental"
TITLE = ImageFont.truetype(os.path.join(FONT_DIR, "DIN Alternate Bold.ttf"), 54)
H1 = ImageFont.truetype(os.path.join(FONT_DIR, "DIN Alternate Bold.ttf"), 28)
H2 = ImageFont.truetype(os.path.join(FONT_DIR, "DIN Alternate Bold.ttf"), 20)
BODY = ImageFont.truetype(os.path.join(FONT_DIR, "Arial.ttf"), 18)
BODY_B = ImageFont.truetype(os.path.join(FONT_DIR, "Arial Bold.ttf"), 19)
SMALL = ImageFont.truetype(os.path.join(FONT_DIR, "Arial.ttf"), 14)
TINY = ImageFont.truetype(os.path.join(FONT_DIR, "Arial.ttf"), 12)
MONO = ImageFont.truetype(os.path.join(FONT_DIR, "Courier New Bold.ttf"), 16)
MONO_SM = ImageFont.truetype(os.path.join(FONT_DIR, "Courier New Bold.ttf"), 13)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


def lum(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def on_color(rgb):
    return (18, 16, 14) if lum(rgb) > 0.45 else (246, 240, 228)


def rgb_str(rgb):
    return "%3d %3d %3d" % rgb


# Wartime reconstructions. Default = working colour for 2D sprites.
# Light / dark = highlight and recess. Source: RAL 840-HR conversions,
# AK Real Colors / surviving chips (mylittlepanzer spectrographic set)
# except 7017, 7027, interiors/markings as noted.

COLORS = [
    # --- 1943-45 three-tone (the set to use first) ---
    dict(
        group="three",
        ral="7028",
        de="Dunkelgelb",
        en="Dark Yellow (registered)",
        when="Aug 1943 – Oct 1944",
        use="Factory base of the three-tone scheme",
        default="#9A8953",
        light="#BBAF7A",
        dark="#73673E",
        note="Use this as the default Dunkelgelb",
    ),
    dict(
        group="three",
        ral="6003",
        de="Olivgrün",
        en="Olive Green",
        when="1943 – 1945",
        use="Disruptive; factory base from Nov 1944",
        default="#39472F",
        light="#6F7A68",
        dark="#283220",
        note="",
    ),
    dict(
        group="three",
        ral="8017",
        de="Rotbraun",
        en="Red Brown / Schokoladenbraun",
        when="1943 – 1945",
        use="Disruptive over Dunkelgelb or Olivgrün",
        default="#4B302B",
        light="#7E6864",
        dark="#35211D",
        note="",
    ),
    # --- Dunkelgelb variants ---
    dict(
        group="gelb",
        ral="7028",
        de="Dunkelgelb nach Muster",
        en="Dark Yellow according to sample",
        when="Feb – Aug 1943",
        use="Early paste / Kursk-era; warmer mustard",
        default="#A39448",
        light="#C3AF6A",
        dark="#7A6F36",
        note="Warmer / more orange than registered 7028",
    ),
    dict(
        group="gelb",
        ral="7028",
        de="Dunkelgelb Ausgabe 1944",
        en="Dark Yellow 1944 issue",
        when="Oct 1944 – 1945",
        use="Later, greyer / darker tan",
        default="#9C8848",
        light="#BDB98C",
        dark="#756530",
        note="Greyer than 1943; not a new RAL number",
    ),
    # --- early war ---
    dict(
        group="early",
        ral="7021",
        de="Dunkelgrau",
        en="Panzergrau / Schwarzgrau",
        when="1937 – Feb 1943",
        use="Early-war base; sole colour from Jul 1940",
        default="#4A4A4C",
        light="#7C7C7E",
        dark="#353536",
        note="Working mid-tone; official chip is darker #2E3234",
    ),
    dict(
        group="early",
        ral="7017",
        de="Dunkelbraun",
        en="Dark Brown",
        when="1937 – 1940",
        use="Cloud / patch over 7021, about 1/3 of surface",
        default="#4A4038",
        light="#6E645C",
        dark="#322B26",
        note="Low contrast with 7021 by design",
    ),
    dict(
        group="early",
        ral="8002",
        de="Erdgelb",
        en="Earth Yellow (wartime)",
        when="1935 – 1937",
        use="Pre-war cloud pattern over grey",
        default="#B69749",
        light="#D4BC8A",
        dark="#8A7136",
        note="Wartime value. Modern RAL 8002 Signalbraun is wrong",
    ),
    # --- DAK ---
    dict(
        group="dak",
        ral="8000",
        de="Grünbraun",
        en="Yellow Brown / Gelbbraun",
        when="Mar 1941 – Apr 1942",
        use="DAK Tropen 1 base (2/3 of vehicle)",
        default="#9B7C52",
        light="#C2A87A",
        dark="#735C3C",
        note="",
    ),
    dict(
        group="dak",
        ral="7008",
        de="Khakigrau",
        en="Khaki Grey / Graugrün",
        when="Mar 1941 – Apr 1942",
        use="DAK Tropen 1 disruptive (1/3)",
        default="#6C6040",
        light="#968D76",
        dark="#4E452D",
        note="",
    ),
    dict(
        group="dak",
        ral="8020",
        de="Sandbraun",
        en="Sand Brown (wartime)",
        when="Mar 1942 – May 1943",
        use="DAK Tropen 2 base (2/3)",
        default="#B68C6B",
        light="#D0B996",
        dark="#8A6750",
        note="Wartime value. Modern RAL 8020 was redefined 1953",
    ),
    dict(
        group="dak",
        ral="7027",
        de="Grau",
        en="Sand Grey / Grüngrau",
        when="Mar 1942 – May 1943",
        use="DAK Tropen 2 disruptive (1/3)",
        default="#9A9170",
        light="#B8B090",
        dark="#6F6850",
        note="Deleted from modern RAL Classic; wartime only",
    ),
    # --- late war primer ---
    dict(
        group="late",
        ral="8012",
        de="Rotbraun",
        en="Red Oxide primer",
        when="Oct 1944 – 1945",
        use="Left as visible base; also camo patches",
        default="#712323",
        light="#9E635F",
        dark="#521717",
        note="Primer showing through late-war factory schemes",
    ),
    dict(
        group="late",
        ral="3009",
        de="Oxidrot",
        en="Oxide Red",
        when="1939 – 1945",
        use="Anti-rust primer (alternate to 8012)",
        default="#703731",
        light="#9A6A64",
        dark="#4A2420",
        note="Modern RAL Classic chip",
    ),
    # --- interiors / equipment / markings ---
    dict(
        group="other",
        ral="1001",
        de="Elfenbein",
        en="Ivory / Beige",
        when="1939 – 1945",
        use="Fighting-compartment interiors",
        default="#D0B084",
        light="#E4D0B0",
        dark="#A88C64",
        note="Modern RAL Classic chip",
    ),
    dict(
        group="other",
        ral="6006",
        de="Feldgrau",
        en="Field Grey",
        when="1935 – 1945",
        use="Equipment, ammo boxes, some softskins",
        default="#40433B",
        light="#6A6E64",
        dark="#2A2C27",
        note="Modern RAL Classic chip",
    ),
    dict(
        group="other",
        ral="9001",
        de="Cremeweiß",
        en="Cream White",
        when="1939 – 1943",
        use="Winter wash / Balkenkreuz / numbers",
        default="#FDF4E3",
        light="#FFFFFF",
        dark="#D4CBB8",
        note="Winter paste over existing camo",
    ),
    dict(
        group="other",
        ral="9005",
        de="Tiefschwarz",
        en="Jet Black",
        when="1939 – 1945",
        use="Markings, tires, tools",
        default="#0A0A0D",
        light="#2A2A2E",
        dark="#000000",
        note="",
    ),
    dict(
        group="other",
        ral="3000",
        de="Feuerrot",
        en="Flame Red",
        when="1939 – 1945",
        use="Tactical numbers, kill rings, flags",
        default="#AB2524",
        light="#C85A58",
        dark="#6E1615",
        note="Modern RAL Classic chip",
    ),
    dict(
        group="other",
        ral="5001",
        de="Grünblau",
        en="Green Blue",
        when="1939 – 1945",
        use="Tactical markings (alternate)",
        default="#1F4764",
        light="#4A7390",
        dark="#122C40",
        note="Modern RAL Classic chip",
    ),
]


SCHEMES = [
    ("1937–40  two-tone", "7021 base + 7017 patches (~2:1)", ["#4A4A4C", "#4A4A4C", "#4A4038"]),
    ("1940–43  Panzergrau", "Overall 7021. No brown after Jul 1940.", ["#4A4A4C"]),
    ("DAK Tropen 1  1941", "8000 base + 7008 patches (~2:1)", ["#9B7C52", "#9B7C52", "#6C6040"]),
    ("DAK Tropen 2  1942", "8020 base + 7027 patches (~2:1)", ["#B68C6B", "#B68C6B", "#9A9170"]),
    ("1943–44  three-tone", "7028 base; 6003 + 8017 field paste", ["#9A8953", "#39472F", "#4B302B"]),
    ("Hinterhalt  Aug 1944", "Same three, factory hard-edge + dots", ["#9A8953", "#39472F", "#4B302B"]),
    ("Primer  Oct 1944", "8012 left showing + 6003 + 7028", ["#712323", "#39472F", "#9A8953"]),
    ("1945  Olivgrün base", "6003 base; 8017 + 7028 hard patches", ["#39472F", "#4B302B", "#9C8848"]),
]


def draw_round_rect(draw, box, fill, radius=10):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def text_w(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def draw_card(draw, x, y, w, h, c):
    d = hex_to_rgb(c["default"])
    li = hex_to_rgb(c["light"])
    dk = hex_to_rgb(c["dark"])

    draw_round_rect(draw, (x, y, x + w, y + h), (28, 25, 22), radius=12)

    pad = 10
    sw_h = 108
    sw = (x + pad, y + pad, x + w - pad, y + pad + sw_h)
    draw.rounded_rectangle(sw, radius=8, fill=d)

    # light / default / dark strip
    strip_y = y + pad + sw_h + 6
    strip_h = 26
    inner_w = w - 2 * pad
    third = inner_w / 3.0
    bands = [
        (li, "LIGHT"),
        (d, "DEFAULT"),
        (dk, "DARK"),
    ]
    for i, (col, label) in enumerate(bands):
        bx0 = x + pad + int(i * third)
        bx1 = x + pad + int((i + 1) * third)
        if i == 0:
            draw.rectangle((bx0, strip_y, bx1, strip_y + strip_h), fill=col)
        elif i == 2:
            draw.rectangle((bx0, strip_y, bx1, strip_y + strip_h), fill=col)
        else:
            draw.rectangle((bx0, strip_y, bx1, strip_y + strip_h), fill=col)
        # labels on the strip
        tc = on_color(col)
        tw = text_w(draw, label, TINY)
        draw.text(
            (bx0 + (bx1 - bx0 - tw) / 2, strip_y + 7),
            label,
            font=TINY,
            fill=tc,
        )

    ty = strip_y + strip_h + 10
    max_tw = w - 2 * pad - 8
    ral = "RAL %s" % c["ral"]
    rw = text_w(draw, ral, MONO)
    draw.text((x + pad + 4, ty), c["de"], font=BODY_B, fill=INK)
    draw.text((x + w - pad - 4 - rw, ty + 2), ral, font=MONO, fill=ACCENT)

    ty += 22
    draw.text((x + pad + 4, ty), c["en"], font=SMALL, fill=INK_DIM)

    ty += 20
    hx = c["default"].upper()
    rgb = "RGB %s" % rgb_str(d)
    draw.text((x + pad + 4, ty), hx, font=MONO, fill=INK)
    hx_w = text_w(draw, hx, MONO)
    draw.text((x + pad + 8 + hx_w, ty + 1), rgb, font=MONO_SM, fill=INK_DIM)

    ty += 20
    draw.text((x + pad + 4, ty), c["when"], font=SMALL, fill=ACCENT)
    ty += 18
    for line in wrap(draw, c["use"], SMALL, max_tw)[:2]:
        draw.text((x + pad + 4, ty), line, font=SMALL, fill=INK_MUTED)
        ty += 16
    if c.get("note"):
        for line in wrap(draw, c["note"], TINY, max_tw)[:2]:
            draw.text((x + pad + 4, ty), line, font=TINY, fill=INK_MUTED)
            ty += 14


def draw_section_label(draw, x, y, text, sub=None):
    draw.text((x, y), text, font=H1, fill=INK)
    if sub:
        draw.text((x, y + 32), sub, font=SMALL, fill=INK_MUTED)
    # rule
    y2 = y + (54 if sub else 38)
    draw.line((x, y2, x + 2384 - 96, y2), fill=RULE, width=1)
    return y2 + 16


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    mx = 48

    # header bar
    draw.rectangle((0, 0, W, 132), fill=(12, 11, 10))
    draw.rectangle((0, 132, W, 136), fill=ACCENT)

    draw.text((mx, 22), "WEHRMACHT  AFV  CAMOUFLAGE", font=TITLE, fill=INK)
    draw.text((mx, 82), "1937  –  1945     ·     wartime reconstructions for sprite painting", font=H2, fill=ACCENT)
    note_r = "Eyedrop the big swatch. LIGHT / DARK = highlight / recess."
    rw = text_w(draw, note_r, SMALL)
    draw.text((W - mx - rw, 28), note_r, font=SMALL, fill=INK_DIM)
    note_r2 = "Modern RAL 7028 / 8002 / 8020 chips are the wrong colours."
    rw2 = text_w(draw, note_r2, SMALL)
    draw.text((W - mx - rw2, 50), note_r2, font=SMALL, fill=INK_MUTED)
    note_r3 = "No hex is ground truth. Factory batches varied ~10%."
    rw3 = text_w(draw, note_r3, SMALL)
    draw.text((W - mx - rw3, 72), note_r3, font=SMALL, fill=INK_MUTED)

    y = 156
    gap = 16
    col_w = (W - 2 * mx - 2 * gap) // 3
    card_h = 314

    # eyedropper strip of every DEFAULT
    y = draw_section_label(draw, mx, y, "EYEDROPPER STRIP", "One square per colour, DEFAULT only. Sample these.")
    n_all = len(COLORS)
    strip_h = 72
    cell = (W - 2 * mx) / float(n_all)
    for i, c in enumerate(COLORS):
        x0 = int(mx + i * cell)
        x1 = int(mx + (i + 1) * cell)
        draw.rectangle((x0, y, x1, y + strip_h), fill=hex_to_rgb(c["default"]))
        tc = on_color(hex_to_rgb(c["default"]))
        label = c["ral"]
        tw = text_w(draw, label, TINY)
        draw.text((x0 + (x1 - x0 - tw) / 2, y + strip_h - 16), label, font=TINY, fill=tc)
    y += strip_h + 24

    # THREE TONE
    y = draw_section_label(
        draw,
        mx,
        y,
        "THE 1943–45 THREE-TONE",
        "Start here for StuG III, Panzer IV H/J, Panther, Tiger, Hetzer, Elefant.",
    )
    three = [c for c in COLORS if c["group"] == "three"]
    for i, c in enumerate(three):
        draw_card(draw, mx + i * (col_w + gap), y, col_w, card_h, c)
    y += card_h + 28

    # DUNKELGELB VARIANTS
    y = draw_section_label(
        draw,
        mx,
        y,
        "DUNKELGELB VARIANTS",
        "Same RAL number, three wartime mixes. Default 7028 (above) is the one to paint with unless you are matching a specific date.",
    )
    gelb = [c for c in COLORS if c["group"] == "gelb"]
    # two cards, left-aligned, same col_w
    for i, c in enumerate(gelb):
        draw_card(draw, mx + i * (col_w + gap), y, col_w, card_h, c)
    y += card_h + 28

    # EARLY
    y = draw_section_label(
        draw,
        mx,
        y,
        "EARLY WAR  1937–1943",
        "Two-tone grey/brown until July 1940, then overall Panzergrau. Existing grey vehicles were not factory-repainted in 1943.",
    )
    early = [c for c in COLORS if c["group"] == "early"]
    for i, c in enumerate(early):
        draw_card(draw, mx + i * (col_w + gap), y, col_w, card_h, c)
    y += card_h + 28

    # DAK
    y = draw_section_label(
        draw,
        mx,
        y,
        "NORTH AFRICA  (DAK)",
        "Tropen 1 (1941): 8000 + 7008. Tropen 2 (from Mar 1942): 8020 + 7027. Use wartime 8020, not the post-1953 chip.",
    )
    dak = [c for c in COLORS if c["group"] == "dak"]
    dak_gap = 12
    dak_w = (W - 2 * mx - 3 * dak_gap) // 4
    for i, c in enumerate(dak):
        draw_card(draw, mx + i * (dak_w + dak_gap), y, dak_w, card_h, c)
    y += card_h + 28

    # LATE
    y = draw_section_label(
        draw,
        mx,
        y,
        "LATE-WAR PRIMER",
        "From October 1944 factories often skipped Dunkelgelb and left red oxide showing as a fourth 'colour'.",
    )
    late = [c for c in COLORS if c["group"] == "late"]
    for i, c in enumerate(late):
        draw_card(draw, mx + i * (col_w + gap), y, col_w, card_h, c)
    y += card_h + 28

    # OTHER
    y = draw_section_label(
        draw,
        mx,
        y,
        "INTERIORS, EQUIPMENT, MARKINGS",
        "Not hull camo, but you will need them on the same vehicles.",
    )
    other = [c for c in COLORS if c["group"] == "other"]
    for i, c in enumerate(other[:3]):
        draw_card(draw, mx + i * (col_w + gap), y, col_w, card_h, c)
    y += card_h + 12
    for i, c in enumerate(other[3:]):
        draw_card(draw, mx + i * (col_w + gap), y, col_w, card_h, c)
    y += card_h + 32

    # SCHEMES
    y = draw_section_label(
        draw,
        mx,
        y,
        "OFFICIAL SCHEME COMBINATIONS",
        "Bars show typical mix, not a pattern. Field units improvised freely after Feb 1943.",
    )

    row_h = 52
    for i, (title, desc, cols) in enumerate(SCHEMES):
        ry = y + i * (row_h + 8)
        draw_round_rect(draw, (mx, ry, W - mx, ry + row_h), (28, 25, 22), radius=8)
        draw.text((mx + 16, ry + 8), title, font=BODY_B, fill=INK)
        draw.text((mx + 16, ry + 28), desc, font=TINY, fill=INK_MUTED)

        bar_x = mx + 640
        bar_w = W - mx - bar_x - 16
        bar_y = ry + 10
        bar_h = 32
        n = len(cols)
        seg = bar_w / float(n)
        for j, hx in enumerate(cols):
            x0 = int(bar_x + j * seg)
            x1 = int(bar_x + (j + 1) * seg)
            rgb = hex_to_rgb(hx)
            draw.rectangle((x0, bar_y, x1, bar_y + bar_h), fill=rgb)
            hx_l = hx.upper()
            tw = text_w(draw, hx_l, TINY)
            if x1 - x0 > tw + 8:
                draw.text(
                    (x0 + (x1 - x0 - tw) / 2, bar_y + 9),
                    hx_l,
                    font=TINY,
                    fill=on_color(rgb),
                )

    y += len(SCHEMES) * (row_h + 8) + 24

    # footer
    foot = [
        "Sources: Heeresmitteilungen 1940 Nr.864, 1943 Nr.181/322, 1944 ambush/primer/Olivgrün orders; RAL 840-HR;",
        "AK Interactive Real Colors of WWII (Kiroff); spectrographic reconstructions of surviving wartime chips.",
        "Do not use modern RAL 7028 (a post-war grey-green). RAL 8002 and 8020 were redefined in 1953.",
        "TWE working set: Dunkelgelb #9A8953  +  Olivgrün #39472F  +  Rotbraun #4B302B  +  Panzergrau #4A4A4C",
    ]
    for i, line in enumerate(foot):
        draw.text((mx, y + i * 18), line, font=SMALL, fill=INK_MUTED)

    # crop leftover empty canvas if we over-allocated
    bbox_bottom = y + 4 * 18 + 40
    if bbox_bottom < H:
        img = img.crop((0, 0, W, bbox_bottom))

    img.save(OUT, "PNG")
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
