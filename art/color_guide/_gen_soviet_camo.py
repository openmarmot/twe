# Red Army WWII AFV colour chart — same layout as german_camo_colors.png

import os
from _chart import render_chart

HERE = os.path.dirname(__file__)

# Working DEFAULT hexes for 2D sprites.
# 4BO is yellower/greener than US Olive Drab. It is not "Russian green" from a hobby pot.

BO = "#55643A"
BO_FRESH = "#4A6B32"
BO_FADED = "#6E6B4A"
B3 = "#3A4A30"
K6 = "#4A3528"
K7 = "#C4A056"
K4 = "#7A7B5C"
RP6 = "#1A1816"
PK = "#4A5840"
WHT = "#F5F2E8"
PRIMER = "#6B3A2E"
IVORY = "#D4C4A0"
STAR = "#B71C1C"
NUM = "#F0EDE4"
OD_LL = "#544F3D"

COLORS = [
    dict(
        group="bo",
        de="4BO  Protective",
        en="Zashchitnyy — factory overall green",
        code="4BO",
        short="4BO",
        when="1938 – 1945",
        use="The default. T-34, T-70, KV, SU, BA-64, almost everything.",
        default=BO,
        note="Use this. Yellower than US OD. Not a bright 'tank green'.",
    ),
    dict(
        group="bo",
        de="4BO  factory-fresh",
        en="New 4BO before dust and sun",
        code="4BO new",
        short="4BO n",
        when="Factory / railhead",
        use="Highlight on a new vehicle. Slightly grassier than in-service 4BO.",
        default=BO_FRESH,
        note="Fresh 4BO can look surprisingly green. It khaki-fades in weeks.",
    ),
    dict(
        group="bo",
        de="4BO  faded",
        en="Dusty khaki-green, in-service",
        code="4BO fade",
        short="4BO f",
        when="Any front, after a few weeks",
        use="Recess / dust coat. How most T-34s actually looked in 1943–45.",
        default=BO_FADED,
        note="Museum T-34s are often this khaki, not the factory green.",
    ),
    dict(
        group="early",
        de="3B  Protective",
        en="Pre-4BO dark olive, 1930s",
        code="3B",
        short="3B",
        when="~1930 – 1938",
        use="BT, T-26, T-28 and other pre-war types still in 1941.",
        default=B3,
        note="Darker and greener than 4BO. Replaced in 1938; stocks lingered.",
    ),
    dict(
        group="camo",
        de="6K  Dark Brown",
        en="Tyomno-korichnevyy",
        code="6K",
        short="6K",
        when="1939 – 1945 (rare after 1941)",
        use="Large brown patches, 15–30% of the vehicle, over 4BO.",
        default=K6,
        note="Earth brown, not German Rotbraun. Meant to read as tree trunks.",
    ),
    dict(
        group="camo",
        de="7K  Yellow Earth",
        en="Zhyolto-zemlistyy / sand",
        code="7K",
        short="7K",
        when="1939 – 1945 (rare after 1941)",
        use="Sand-ochre patches, 15–30%, over 4BO. Ploughed fields, roads.",
        default=K7,
        note="Lighter and more yellow than German Dunkelgelb. Paste, not factory enamel.",
    ),
    dict(
        group="camo",
        de="4K  Grey-Earth",
        en="Sero-zemlistyy — the 'fourth colour'",
        code="4K",
        short="4K",
        when="Factory instruction, uncommon",
        use="Grey-green earth in some 4-colour factory diagrams.",
        default=K4,
        note="Documented; almost never the look of a typical T-34. Optional.",
    ),
    dict(
        group="camo",
        de="6RP  Black",
        en="Black as a 6K stand-in",
        code="6RP",
        short="6RP",
        when="1939 trials; occasional field use",
        use="Black patches instead of 6K when brown paste was short.",
        default=RP6,
        note="A substitute, not a standard fourth camo colour.",
    ),
    dict(
        group="other",
        de="Protective K",
        en="Softskin / equipment green",
        code="K",
        short="K",
        when="1930s – 1945",
        use="Trucks, ammo boxes, some primer. Close to 4BO, slightly greyer.",
        default=PK,
        note="Not a tank factory colour. Use on ZIS-5, crates, jerrycans.",
    ),
    dict(
        group="other",
        de="White B",
        en="Winter distemper",
        code="B",
        short="White B",
        when="Winter, every year",
        use="Washable white over 4BO. Moscow 1941, all later winters.",
        default=WHT,
        note="Officially not a solid coat. Crews still painted whole tanks white.",
    ),
    dict(
        group="other",
        de="Red ochre primer",
        en="Surik / anti-rust",
        code="primer",
        short="Primer",
        when="1930s – 1945",
        use="Chips, unpainted fittings, some factory undercoat.",
        default=PRIMER,
        note="Brick red-brown. Same job as German 8012, different mix.",
    ),
    dict(
        group="other",
        de="Slonovaya kost",
        en="Ivory fighting-compartment interior",
        code="ivory",
        short="Ivory",
        when="1930s – 1945",
        use="Turret and fighting-compartment interior on many AFVs.",
        default=IVORY,
        note="Floors and engine bays were often 4BO or primer, not ivory.",
    ),
    dict(
        group="mark",
        de="Red star",
        en="National marking",
        code="star",
        short="Star",
        when="1930s – 1945",
        use="Stars were less common on tanks than numbers. Use sparingly.",
        default=STAR,
        note="Many T-34s had only a white turret number, no star.",
    ),
    dict(
        group="mark",
        de="White number",
        en="Turret / hull tactical number",
        code="white",
        short="Number",
        when="1930s – 1945",
        use="The usual marking. Slogans were also white.",
        default=NUM,
        note="Hand-painted, often crude. Size and font varied by unit.",
    ),
    dict(
        group="mark",
        de="Lend-lease OD",
        en="US Olive Drab left on Shermans, Valentines, etc.",
        code="US OD",
        short="LL OD",
        when="1942 – 1945",
        use="M3, Sherman, Universal Carrier as delivered. Sometimes oversprayed 4BO.",
        default=OD_LL,
        note="Same hex as the US chart. British vehicles arrived in SCC 2 / SCC 15.",
    ),
]

SCHEMES = [
    ("1938–45  overall 4BO", "The default. Most T-34s, SU-85/100, T-70, KV.", [BO]),
    ("1939–41  three-tone", "4BO ~50% + 6K 15–30% + 7K 15–30%. Official, uncommon.", [BO, K6, K7]),
    ("Two-tone  4BO + 6K", "Green + large brown patches. Leningrad, 1942–43 photos.", [BO, BO, K6]),
    ("Two-tone  4BO + 7K", "Green + sand-ochre. Some 1943 T-34s, Leningrad.", [BO, BO, K7]),
    ("4-tone  (rare)", "4BO + 4K + 6K + 7K factory diagrams. Almost never typical.", [BO, K4, K6, K7]),
    ("Winter  White B", "Washable white over 4BO. Remove when the snow goes.", [WHT, WHT, BO]),
    ("Lend-lease", "Left in US OD or British SCC, or oversprayed 4BO.", [OD_LL, OD_LL, BO]),
]


def main():
    render_chart(dict(
        title="RED ARMY  AFV  CAMOUFLAGE",
        period_line="1930  –  1945     ·     wartime reconstructions for sprite painting",
        notes=[
            "Eyedrop the big swatch. LIGHT / DARK = highlight / recess.",
            "4BO is the one colour for almost every T-34. Multi-colour was official but rare.",
            "No hex is ground truth. 4BO batches and fade varied widely.",
        ],
        colors=COLORS,
        sections=[
            dict(
                title="THE DEFAULT — 4BO PROTECTIVE GREEN",
                sub="Start here for T-34, T-70, KV-2, SU-76, SU-85, SU-100, BA-64. From 1942 most vehicles stayed overall 4BO.",
                group="bo",
                cols=3,
            ),
            dict(
                title="PRE-WAR BASE",
                sub="3B is the 1930s green. Anything built before 1938, and some still fighting in 1941, may be 3B not 4BO.",
                group="early",
                cols=3,
            ),
            dict(
                title="1939–41 DISRUPTIVE PASTE",
                sub="Issued as paste, thinned with drying oil and gasoline. 4BO stays the majority. After 1941 this is the exception, not the rule.",
                group="camo",
                cols=4,
            ),
            dict(
                title="PRIMER, INTERIORS, WINTER, SOFTSKINS",
                sub="Not hull camo, but you will need them on the same vehicles.",
                group="other",
                cols=4,
            ),
            dict(
                title="MARKINGS AND LEND-LEASE",
                sub="A white number is more typical than a red star. Lend-lease often kept the Allied factory colour.",
                group="mark",
                cols=3,
            ),
        ],
        scheme_sub="Bars show typical mix, not a pattern. After summer 1943, overall 4BO again dominated.",
        schemes=SCHEMES,
        footer=[
            "Sources: 1939 NKTP / GABTU camo instructions; 1941 three-colour order (4BO 45–50%, 7K, 6K);",
            "Moschansky; Tank Archives (4K 'fourth colour'); AK Interactive Real Colors of WWII (Skulski).",
            "7K is yellow-earth, not 'green-black' (a common mistranslation). 4BO is not US Olive Drab.",
            "TWE working set: 4BO #55643A  +  6K #4A3528  +  7K #C4A056  +  White B #F5F2E8",
        ],
        outfile=os.path.join(HERE, "soviet_camo_colors.png"),
    ))


if __name__ == "__main__":
    main()
