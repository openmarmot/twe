# one-shot generator for weathering_colors.png
# working colours for sprite weathering; not a paint-chip standard
#
# Hue rule, so the families stay eyedroppable next to the faction charts:
#   rust  red-orange   (R well above G)
#   oil   warm brown   (R > G > B, yellower than rust)
#   soot  blue-grey    (B >= G >= R)
#   earth grey or dull red-brown, never as red as rust and never as yellow as 7K
# Grease is the one green, and it is darker than Olivgrün / 4BO.
# Wet mud is darker than Soviet 6K. There is no separate black-soil chip.

import os
from _chart import render_chart, hex_to_rgb

HERE = os.path.dirname(__file__)

# Rust. Fresh is the only saturated one. Body is the default. Stain is runoff.
RST_FRESH = "#E05820"
RST_BODY = "#C05028"
RST_STAIN = "#E08858"

# Oil. Fresh is dark mustard, not black, so a leak cannot become carbon.
OIL_FRESH = "#5C3C0C"
OIL_USED = "#8C5C20"
OIL_DRIED = "#A87838"
OIL_GREASE = "#16321E"

# Soot. Cool the whole way. Carbon is a dark slate, not a marking black.
SOT_CARBON = "#2A3840"
SOT_EXHAUST = "#4A5C6A"
SOT_SMOKE = "#70808C"
SOT_ASH = "#A8B6BE"

# Earth. Dust is a light grey coat. Mud is darker than the brown camos.
ERT_PALE = "#D8D8D2"
ERT_FIELD = "#A8A498"
ERT_DRY = "#807868"
ERT_WET = "#32261E"
ERT_CLAY = "#A05848"

# Faction DEFAULT chips these had to stay clear of. Printed only.
CAMO_NEAR = [
    ("DG 7028", "#9A8953"),
    ("OG 6003", "#39472F"),
    ("RB 8017", "#4B302B"),
    ("PG 7021", "#4A4A4C"),
    ("KG 7008", "#6C6040"),
    ("ivory 1001", "#D0B084"),
    ("US OD", "#544F3D"),
    ("US sand", "#A6977D"),
    ("US earth red", "#7A4A3C"),
    ("US field drab", "#6B5638"),
    ("US red", "#A83932"),
    ("insig blue", "#1E3A5F"),
    ("4BO", "#55643A"),
    ("6K", "#4A3528"),
    ("7K", "#C4A056"),
    ("soviet ivory", "#D4C4A0"),
    ("marking black", "#1C1C1C"),
]


COLORS = [
    dict(
        group="rust",
        de="Fresh rust",
        en="New oxide on bare metal",
        code="RST-1",
        short="RST1",
        when="Chip lip or a fresh scratch",
        use="The only saturated rust. A few pixels on the edge of a chip.",
        default=RST_FRESH,
        note="A panel painted this colour is too much rust.",
    ),
    dict(
        group="rust",
        de="Rust",
        en="Working red-brown",
        code="RST-2",
        short="RST2",
        when="Welds, fenders, torn plate",
        use="Default rust. Redder than clay, darker than the stain under it.",
        default=RST_BODY,
        note="The dark band is the pit. Rotbraun and red primer stay paint.",
    ),
    dict(
        group="rust",
        de="Rust stain",
        en="Light orange runoff",
        code="RST-3",
        short="RST3",
        when="Vertical streak below the rust",
        use="Wider and lighter than the rust that feeds it. Vertical only.",
        default=RST_STAIN,
        note="Not ivory, and not dust. Dried oil is yellower.",
    ),
    dict(
        group="oil",
        de="Fresh oil",
        en="Wet petroleum",
        code="OIL-1",
        short="OIL1",
        when="Caps, seals, a fresh drip",
        use="Darkest oil. Mustard-brown, so a leak does not read as soot.",
        default=OIL_FRESH,
        note="Carbon is the blue-grey. This one stays warm.",
    ),
    dict(
        group="oil",
        de="Used oil",
        en="The usual streak",
        code="OIL-2",
        short="OIL2",
        when="Engine deck, road wheels",
        use="Default oil. Short runs that start at a fresh drip or a seal.",
        default=OIL_USED,
        note="Mud is greyer and sits lower on the hull.",
    ),
    dict(
        group="oil",
        de="Dried oil",
        en="Amber halo",
        code="OIL-3",
        short="OIL3",
        when="Edge of a leak",
        use="Wider than the wet centre. The last step of a leak.",
        default=OIL_DRIED,
        note="Darker and more orange than Soviet 7K. 7K is paint.",
    ),
    dict(
        group="oil",
        de="Grease",
        en="Dark green point",
        code="OIL-4",
        short="OIL4",
        when="Hubs, tow hooks, MG ball",
        use="A point of colour, not a streak. Darker than Olivgrün and 4BO.",
        default=OIL_GREASE,
        note="The only green in the set. It does not run far.",
    ),
    dict(
        group="soot",
        de="Carbon",
        en="Dark slate at the opening",
        code="SOT-1",
        short="SOT1",
        when="Muzzle crown, exhaust lip",
        use="Default soot. Blue-grey, right at the hole.",
        default=SOT_CARBON,
        note="Not a marking black, and not insignia blue.",
    ),
    dict(
        group="soot",
        de="Exhaust soot",
        en="Mid blue-grey",
        code="SOT-2",
        short="SOT2",
        when="Short plume beside the pipe",
        use="Collected soot around the outlet, past the carbon.",
        default=SOT_EXHAUST,
        note="Bluer than Panzergrau. Panzergrau is paint.",
    ),
    dict(
        group="soot",
        de="Smoke",
        en="Cordite and powder",
        code="SOT-3",
        short="SOT3",
        when="Breech, cases, barrel",
        use="Lighter blue-grey film. Powder residue, not a grey panel.",
        default=SOT_SMOKE,
        note="Still cool. Field dust is the one with brown in it.",
    ),
    dict(
        group="soot",
        de="Ash",
        en="Light soot dust",
        code="SOT-4",
        short="SOT4",
        when="Thin coat downwind of the pipe",
        use="The wide, faint end of an exhaust stain.",
        default=SOT_ASH,
        note="No brown in it. Field dust is the grey-tan one.",
    ),
    dict(
        group="earth",
        de="Pale dust",
        en="Dry-climate coat",
        code="ERT-1",
        short="ERT1",
        when="Upper surfaces, desert and high summer",
        use="Light neutral film. Libya, Sicily, a long dry spell.",
        default=ERT_PALE,
        note="Greyer than interior ivory, and lighter than any camo tan.",
    ),
    dict(
        group="earth",
        de="Field dust",
        en="Everyday grey film",
        code="ERT-2",
        short="ERT2",
        when="Upper surfaces, Europe",
        use="Default dust. Neutral grey over any camo, paint still reads under it.",
        default=ERT_FIELD,
        note="US Sand is paint, and tanner. This is dust.",
    ),
    dict(
        group="earth",
        de="Dry earth",
        en="Caked mud",
        code="ERT-3",
        short="ERT3",
        when="Lower hull, dried splash",
        use="The top of a mud splash after it dries. Dull grey-brown.",
        default=ERT_DRY,
        note="Dried oil is more orange. Khakigrau is paint.",
    ),
    dict(
        group="earth",
        de="Wet mud",
        en="Dark soil, lower hull",
        code="ERT-4",
        short="ERT4",
        when="Tracks, belly, lower hull",
        use="The dark earth, including black soil and rasputitsa.",
        default=ERT_WET,
        note="Darker than Soviet 6K. 6K is paint. Oil is yellower.",
    ),
    dict(
        group="earth",
        de="Clay",
        en="Red soil",
        code="ERT-5",
        short="ERT5",
        when="Where wet mud would be, on red ground",
        use="Italy and other red soil. Same places as wet mud.",
        default=ERT_CLAY,
        note="Duller than rust. Earth Red No. 8 is paint.",
    ),
]


SCHEMES = [
    ("Rust chip", "Body, then fresh on the lip only. Fresh stays the smallest mark.", [RST_BODY, RST_BODY, RST_FRESH]),
    ("Rust streak", "Body at the source. Stain below it, wider than the rust.", [RST_BODY, RST_STAIN, RST_STAIN]),
    ("Oil leak", "Fresh core, used streak, dried halo at the edge.", [OIL_FRESH, OIL_USED, OIL_DRIED]),
    ("Grease point", "Grease on the part. Used oil only if it has run.", [OIL_GREASE, OIL_GREASE, OIL_USED]),
    ("Exhaust", "Carbon at the lip, exhaust beside it, ash downwind.", [SOT_CARBON, SOT_EXHAUST, SOT_ASH]),
    ("Muzzle / breech", "Carbon on the crown. Smoke along the barrel and breech.", [SOT_CARBON, SOT_SMOKE]),
    ("Dry dust", "Pale in the desert, field dust in Europe, dry earth low.", [ERT_PALE, ERT_FIELD, ERT_DRY]),
    ("Temperate mud", "Wet mud in the tracks and on the belly. Dry earth at the splash.", [ERT_WET, ERT_WET, ERT_DRY]),
    ("Red soil", "Clay where the mud would be. Pale dust still owns the top.", [ERT_CLAY, ERT_CLAY, ERT_PALE]),
]


def _dist(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def report_near(colors):
    """Print default pairs, and camo defaults, that sit close together."""
    named = [(c["code"], hex_to_rgb(c["default"])) for c in colors]
    hits = []
    for i, (na, ra) in enumerate(named):
        for nb, rb in named[i + 1 :]:
            d = _dist(ra, rb)
            if d < 40:
                hits.append((d, na, nb))
    for d, na, nb in sorted(hits):
        print("near  %5.1f  %s  %s" % (d, na, nb))
    for code, rgb in named:
        for cname, hx in CAMO_NEAR:
            d = _dist(rgb, hex_to_rgb(hx))
            if d < 36:
                print("camo  %5.1f  %s  %s" % (d, code, cname))
    if not hits:
        print("near  none under 40")


def main():
    report_near(COLORS)
    render_chart(dict(
        title="WEATHERING",
        period_line="Rust  ·  oil  ·  soot  ·  earth     ·     one working set for every nation",
        notes=[
            "Eyedrop the big swatch. LIGHT / DARK = highlight / recess.",
            "Soot is blue-grey. Oil is brown. Earth is grey or dull red, never rust-orange.",
            "Start with four: RST-2 rust, OIL-2 oil, SOT-1 soot, ERT-2 dust.",
        ],
        colors=COLORS,
        sections=[
            dict(
                title="RUST",
                sub="Red-orange only. Fresh is a chip lip. Body is the rust you paint. Stain is the runoff under it.",
                group="rust",
                cols=3,
            ),
            dict(
                title="OIL",
                sub="Warm browns, plus grease for a point of dark green. Fresh oil stays brown so it never matches carbon.",
                group="oil",
                cols=4,
            ),
            dict(
                title="SOOT",
                sub="Cool greys. Carbon at the opening, ash at the wide thin end. None of these are Panzergrau or oil.",
                group="soot",
                cols=4,
            ),
            dict(
                title="EARTH",
                sub="Dust is a light grey coat over the camo. Wet mud is the dark soil, including black earth. Mud stays low on the hull.",
                group="earth",
                cols=3,
            ),
        ],
        scheme_title="HOW THEY STACK",
        scheme_sub="Left to right is source to outer edge. A stack for one mark, not a camouflage pattern.",
        schemes=SCHEMES,
        footer=[
            "Working colours for TWE sprites. Not a manufacturer chip. Real dirt varied; this set is so the art does not.",
            "One family per mark. A rust streak is not oiled. Mud is not soot. Dust is thin enough that the camo still reads.",
            "Grease is the only green, darker than Olivgrün and 4BO. Clay is soil. Rust is metal. Ash has no brown; field dust does.",
            "TWE working set: Rust #C05028  +  Used oil #8C5C20  +  Carbon #2A3840  +  Field dust #A8A498",
        ],
        outfile=os.path.join(HERE, "weathering_colors.png"),
    ))


if __name__ == "__main__":
    main()
