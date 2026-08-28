# US Army / USMC WWII AFV colour chart — same layout as german_camo_colors.png

import os
from _chart import render_chart

HERE = os.path.dirname(__file__)

# Working DEFAULT hexes: wartime reconstructions for 2D sprites.
# FS numbers are the closest postwar chip, not a wartime identity.
# OD 9/22 closest chip is FS 33070 (#544F3D). Light/dark auto-filled.

OD = "#544F3D"
OD_FADED = "#6E6954"
OD_319 = "#4E4A38"
EY = "#C39B69"
SAND = "#A6977D"
ER = "#7A4A3C"
EB = "#5A4830"
FD = "#6B5638"
LG = "#6E8048"
BLK = "#1C1C1C"
WHT = "#F4F0E4"
PRIMER = "#6E3A32"
INT = "#7A8B52"
IVORY = "#D4C8A8"
INS_W = "#F0EEE6"
INS_B = "#1E3A5F"
INS_R = "#A83932"
INS_Y = "#E8A317"

COLORS = [
    dict(
        group="od",
        de="Olive Drab",
        en="Lustreless Olive Drab No. 9 / No. 22",
        code="No. 9 / 22",
        short="OD 9",
        when="Oct 1940 – 1945",
        use="Factory overall colour. Sherman, Jeep, M3, Staghound.",
        default=OD,
        note="Closest chip FS 33070. Browner than Tamiya XF-62 looks now.",
    ),
    dict(
        group="od",
        de="Olive Drab, faded",
        en="Sun-bleached in-service OD",
        code="No. 9 faded",
        short="OD fade",
        when="Any theatre, weeks in sun",
        use="Highlight / dust coat over factory OD. Vehicles in the field.",
        default=OD_FADED,
        note="OD is a darkened yellow. Fade shifts it khaki, not bright green.",
    ),
    dict(
        group="od",
        de="Olive Drab No. 319",
        en="Specification 3-1F reformulation",
        code="No. 319",
        short="OD 319",
        when="Apr 1943 – 1945",
        use="Same hue as No. 9/22; held colour better, so looks darker in photos.",
        default=OD_319,
        note="Not a new colour. Use No. 9 unless you are matching a late-war chip.",
    ),
    dict(
        group="desert",
        de="Earth Yellow",
        en="Disruptive sand-yellow",
        code="No. 6",
        short="EY 6",
        when="1942 – 1944",
        use="Sicily (Husky) and North Africa over OD. ~1/3 of the vehicle.",
        default=EY,
        note="Closest chip FS 30257. The usual 'sand stripe on a Sherman'.",
    ),
    dict(
        group="desert",
        de="Sand",
        en="Desert sand / Light Stone stand-in",
        code="No. 3",
        short="Sand",
        when="1942 – 1943",
        use="North Africa desert pattern; also USMC Pacific disruptive.",
        default=SAND,
        note="Closest chip FS 30277. Early Torch units also borrowed British Light Stone.",
    ),
    dict(
        group="desert",
        de="Earth Red",
        en="Reddish desert earth",
        code="No. 8",
        short="ER 8",
        when="1944 spec; rare in action",
        use="FM 5-20B red-desert pattern over OD. Little 1944–45 desert combat.",
        default=ER,
        note="Closest chip FS 30117. Redder than German Rotbraun 8017.",
    ),
    dict(
        group="disrupt",
        de="Black",
        en="Disruptive black / No. 10",
        code="No. 10",
        short="Black",
        when="1944 – 1945 NW Europe",
        use="Hard-edge bands and patches over OD after Normandy.",
        default=BLK,
        note="In photos this often reads as dark grey. Do not paint glossy.",
    ),
    dict(
        group="disrupt",
        de="Light Green",
        en="ANA 611 / Interior Green used as camo",
        code="No. 1",
        short="LG 1",
        when="Occasional 1944–45",
        use="Ad-hoc temperate patches, sometimes with black, over OD.",
        default=LG,
        note="Same hue as US aircraft Interior Green, FS 34151.",
    ),
    dict(
        group="disrupt",
        de="Field Drab",
        en="Dark earth / drab brown",
        code="No. 4",
        short="FD 4",
        when="1943 – 1945",
        use="Earth tone in FM 5-20B temperate / desert mixes.",
        default=FD,
        note="Closest chip FS 30118. Close to RAF Dark Earth.",
    ),
    dict(
        group="disrupt",
        de="Earth Brown",
        en="Dark brown earth",
        code="No. 5",
        short="EB 5",
        when="1943 – 1945",
        use="Extra earth in some Engineer / ad-hoc patterns.",
        default=EB,
        note="Closest chip FS 30099. Darker and cooler than Earth Red.",
    ),
    dict(
        group="other",
        de="White, winter",
        en="Washable white distemper",
        code="No. 11",
        short="White",
        when="Winter 1944–45",
        use="Bulge / Ardennes wash over OD. Patchy on purpose.",
        default=WHT,
        note="Meant to come off. Leave OD showing in wear.",
    ),
    dict(
        group="other",
        de="Red oxide primer",
        en="Anti-rust primer",
        code="primer",
        short="Primer",
        when="1939 – 1945",
        use="Showing in chips and on unpainted fittings.",
        default=PRIMER,
        note="US primer is a brick red-brown, not German 8012.",
    ),
    dict(
        group="other",
        de="Interior Green",
        en="Zinc chromate / ANA 611",
        code="FS 34151",
        short="Int Grn",
        when="1939 – 1945",
        use="Engine bays, some fighting-compartment primer.",
        default=INT,
        note="Early hull interiors were often just OD. This is the yellow-green.",
    ),
    dict(
        group="other",
        de="Ivory interior",
        en="Late fighting-compartment off-white",
        code="ivory",
        short="Ivory",
        when="Mid – late war",
        use="Some late interiors / stowage bins. Not universal.",
        default=IVORY,
        note="Most US AFV interiors stayed OD. Use sparingly.",
    ),
    dict(
        group="mark",
        de="Insignia White",
        en="Stars, numbers, allied recognition",
        code="FS 37875",
        short="Star W",
        when="1939 – 1945",
        use="White star, bumper codes, air ID panels.",
        default=INS_W,
        note="Stars were often painted out in NW Europe after 1944.",
    ),
    dict(
        group="mark",
        de="Insignia Blue",
        en="Star disc / roundel blue",
        code="FS 35044",
        short="Star B",
        when="1942 – 1943 (star-in-circle)",
        use="Blue disc behind the white star on early-war vehicles.",
        default=INS_B,
        note="Dropped for the plain white star in most ETO units.",
    ),
    dict(
        group="mark",
        de="Insignia Red",
        en="Early star / warning",
        code="FS 31136",
        short="Star R",
        when="Pre-1942 star; later warnings",
        use="Red centre of the pre-war star; fire bottles, flags.",
        default=INS_R,
        note="The red-centred star was dropped after Pearl Harbor confusion.",
    ),
    dict(
        group="mark",
        de="Insignia Yellow",
        en="Air ID / bridging plate",
        code="FS 33538",
        short="Yellow",
        when="1939 – 1945",
        use="Aircraft ID, some bridging discs, stencils.",
        default=INS_Y,
        note="High-visibility yellow. Not a hull camo colour.",
    ),
]

SCHEMES = [
    ("1940–45  overall OD", "The default. Sherman, Jeep, M3, almost everything.", [OD]),
    ("N. Africa  1942–43", "OD base + Earth Yellow or Sand patches (ad hoc).", [OD, OD, EY]),
    ("Sicily  Husky 1943", "OD + Earth Yellow No. 6, the common two-tone.", [OD, OD, EY]),
    ("NW Europe  1944–45", "OD + Black No. 10 hard-edge bands (FM 5-20B).", [OD, OD, BLK]),
    ("Desert  FM 5-20B", "OD + Earth Red or Sand. Little late-war desert use.", [OD, ER, SAND]),
    ("Winter  1944–45", "Washable white over OD. Never a clean coat.", [WHT, WHT, OD]),
    ("Pacific  USMC", "OD + Sand / Earth Yellow. USMC used disruptive more.", [OD, SAND, EY]),
]


def main():
    render_chart(dict(
        title="U.S. ARMY  AFV  CAMOUFLAGE",
        period_line="1940  –  1945     ·     wartime reconstructions for sprite painting",
        notes=[
            "Eyedrop the big swatch. LIGHT / DARK = highlight / recess.",
            "FS numbers are postwar closest chips. Wartime OD has no exact FS.",
            "No hex is ground truth. OD varied by maker and faded in weeks.",
        ],
        colors=COLORS,
        sections=[
            dict(
                title="THE DEFAULT — OLIVE DRAB",
                sub="Start here for Sherman, Willys MB, M3 half-track, M3 37mm, Staghound. Almost every US vehicle left the factory in overall OD.",
                group="od",
                cols=3,
            ),
            dict(
                title="NORTH AFRICA AND SICILY",
                sub="Disruptive sand/earth over OD. Torch units also used British desert paints when US stocks were short.",
                group="desert",
                cols=3,
            ),
            dict(
                title="1944 DISRUPTIVE  (FM 5-20B)",
                sub="Engineer manual, April 1944. Temperate pattern is OD + black. Light green and field drab show up ad hoc.",
                group="disrupt",
                cols=4,
            ),
            dict(
                title="PRIMER, INTERIORS, WINTER",
                sub="Not hull camo, but you will need them on the same vehicles.",
                group="other",
                cols=4,
            ),
            dict(
                title="MARKINGS",
                sub="White star is the late-war default. Blue disc is 1942–43. Red-centred star is pre-war only.",
                group="mark",
                cols=4,
            ),
        ],
        scheme_sub="Bars show typical mix, not a pattern. Field units improvised, especially in North Africa.",
        schemes=SCHEMES,
        footer=[
            "Sources: US Spec 3-1 / 3-1F; FM 5-21 (1942) and FM 5-20B (Apr 1944); Zaloga on Olive Drab;",
            "AK Interactive Real Colors (Zaloga); closest FS chips 33070 (OD), 30257 (Earth Yellow), 30277 (Sand), 30117 (Earth Red).",
            "Do not use postwar FS 34087 / 24087 as wartime OD — those are later reformulations.",
            "TWE working set: Olive Drab #544F3D  +  Earth Yellow #C39B69  +  Black #1C1C1C  +  White #F4F0E4",
        ],
        outfile=os.path.join(HERE, "us_camo_colors.png"),
    ))


if __name__ == "__main__":
    main()
