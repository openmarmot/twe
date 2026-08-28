# shared layout for AFV colour charts (german / us / soviet)

import os
from PIL import Image, ImageDraw, ImageFont

W = 2480
BG = (18, 16, 14)
INK = (236, 228, 214)
INK_DIM = (168, 158, 142)
INK_MUTED = (120, 112, 100)
RULE = (58, 52, 44)
ACCENT = (196, 168, 96)
CARD_BG = (28, 25, 22)

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


def rgb_to_hex(rgb):
    return "#%02X%02X%02X" % rgb


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


def lum(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def on_color(rgb):
    return (18, 16, 14) if lum(rgb) > 0.45 else (246, 240, 228)


def rgb_str(rgb):
    return "%3d %3d %3d" % rgb


def fill_shades(c):
    d = hex_to_rgb(c["default"])
    if "light" not in c:
        c["light"] = rgb_to_hex(mix(d, (255, 255, 255), 0.30))
    if "dark" not in c:
        c["dark"] = rgb_to_hex(mix(d, (0, 0, 0), 0.35))
    return c


def color_code(c):
    if "code" in c:
        return c["code"]
    return "RAL %s" % c["ral"]


def color_short(c):
    if "short" in c:
        return c["short"]
    if "ral" in c:
        return c["ral"]
    return c.get("code", "")


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


def draw_round_rect(draw, box, fill, radius=10):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_card(draw, x, y, w, h, c):
    fill_shades(c)
    d = hex_to_rgb(c["default"])
    li = hex_to_rgb(c["light"])
    dk = hex_to_rgb(c["dark"])

    draw_round_rect(draw, (x, y, x + w, y + h), CARD_BG, radius=12)

    pad = 10
    sw_h = 108
    sw = (x + pad, y + pad, x + w - pad, y + pad + sw_h)
    draw.rounded_rectangle(sw, radius=8, fill=d)

    strip_y = y + pad + sw_h + 6
    strip_h = 26
    inner_w = w - 2 * pad
    third = inner_w / 3.0
    bands = [(li, "LIGHT"), (d, "DEFAULT"), (dk, "DARK")]
    for i, (col, label) in enumerate(bands):
        bx0 = x + pad + int(i * third)
        bx1 = x + pad + int((i + 1) * third)
        draw.rectangle((bx0, strip_y, bx1, strip_y + strip_h), fill=col)
        tc = on_color(col)
        tw = text_w(draw, label, TINY)
        draw.text((bx0 + (bx1 - bx0 - tw) / 2, strip_y + 7), label, font=TINY, fill=tc)

    ty = strip_y + strip_h + 10
    max_tw = w - 2 * pad - 8
    code = color_code(c)
    rw = text_w(draw, code, MONO)
    draw.text((x + pad + 4, ty), c["de"], font=BODY_B, fill=INK)
    draw.text((x + w - pad - 4 - rw, ty + 2), code, font=MONO, fill=ACCENT)

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


def draw_section_label(draw, x, y, text, sub, canvas_w):
    draw.text((x, y), text, font=H1, fill=INK)
    if sub:
        draw.text((x, y + 32), sub, font=SMALL, fill=INK_MUTED)
    y2 = y + (54 if sub else 38)
    draw.line((x, y2, canvas_w - x, y2), fill=RULE, width=1)
    return y2 + 16


def render_chart(spec):
    """
    spec keys:
      title, period_line, notes (3 strings), outfile
      colors, sections (list of {title, sub, group, cols}),
      schemes (list of (title, desc, hexes)),
      footer (list of strings)
    """
    colors = [fill_shades(dict(c)) for c in spec["colors"]]
    mx = 48
    gap = 16
    col_w = (W - 2 * mx - 2 * gap) // 3
    card_h = 314
    H = 5200
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, W, 132), fill=(12, 11, 10))
    draw.rectangle((0, 132, W, 136), fill=ACCENT)

    draw.text((mx, 22), spec["title"], font=TITLE, fill=INK)
    draw.text((mx, 82), spec["period_line"], font=H2, fill=ACCENT)
    notes = spec["notes"]
    y_note = 28
    for line in notes:
        rw = text_w(draw, line, SMALL)
        fill = INK_DIM if y_note == 28 else INK_MUTED
        font = SMALL
        draw.text((W - mx - rw, y_note), line, font=font, fill=fill)
        y_note += 22

    y = 156

    y = draw_section_label(
        draw, mx, y, "EYEDROPPER STRIP", "One square per colour, DEFAULT only. Sample these.", W
    )
    n_all = len(colors)
    strip_h = 72
    cell = (W - 2 * mx) / float(n_all)
    for i, c in enumerate(colors):
        x0 = int(mx + i * cell)
        x1 = int(mx + (i + 1) * cell)
        draw.rectangle((x0, y, x1, y + strip_h), fill=hex_to_rgb(c["default"]))
        tc = on_color(hex_to_rgb(c["default"]))
        label = color_short(c)
        tw = text_w(draw, label, TINY)
        draw.text((x0 + (x1 - x0 - tw) / 2, y + strip_h - 16), label, font=TINY, fill=tc)
    y += strip_h + 24

    for section in spec["sections"]:
        group = [c for c in colors if c["group"] == section["group"]]
        if not group:
            continue
        y = draw_section_label(draw, mx, y, section["title"], section.get("sub"), W)
        cols = section.get("cols") or 3
        n_gap = max(cols - 1, 0)
        card_w = (W - 2 * mx - n_gap * gap) // cols
        row = 0
        col_i = 0
        for c in group:
            if col_i == cols:
                col_i = 0
                row += 1
            cx = mx + col_i * (card_w + gap)
            cy = y + row * (card_h + 12)
            draw_card(draw, cx, cy, card_w, card_h, c)
            col_i += 1
        rows = row + 1
        y += rows * (card_h + 12) + 16

    if spec.get("schemes"):
        y = draw_section_label(
            draw,
            mx,
            y,
            "OFFICIAL SCHEME COMBINATIONS",
            spec.get("scheme_sub", "Bars show typical mix, not a pattern."),
            W,
        )
        row_h = 52
        for i, (title, desc, cols_hex) in enumerate(spec["schemes"]):
            ry = y + i * (row_h + 8)
            draw_round_rect(draw, (mx, ry, W - mx, ry + row_h), CARD_BG, radius=8)
            draw.text((mx + 16, ry + 8), title, font=BODY_B, fill=INK)
            draw.text((mx + 16, ry + 28), desc, font=TINY, fill=INK_MUTED)
            bar_x = mx + 640
            bar_w = W - mx - bar_x - 16
            bar_y = ry + 10
            bar_h = 32
            n = len(cols_hex)
            seg = bar_w / float(n)
            for j, hx in enumerate(cols_hex):
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
        y += len(spec["schemes"]) * (row_h + 8) + 24

    for i, line in enumerate(spec.get("footer", [])):
        draw.text((mx, y + i * 18), line, font=SMALL, fill=INK_MUTED)

    bbox_bottom = y + 18 * max(len(spec.get("footer", [])), 1) + 40
    img = img.crop((0, 0, W, min(bbox_bottom, H)))
    out = spec["outfile"]
    img.save(out, "PNG")
    print("wrote", out, img.size)
    return out
