"""
repo : https://github.com/openmarmot/twe

notes :

built-in tactical scenarios. written into the scenario_data sqlite table
on load (upsert by name). extra rows added directly to sqlite are kept.

squad lists use "Squad Name:count" entries, comma separated.
map_areas is a comma list of: town, airport, rail_yard

random_points is a small battlegroup_generator budget added on top of
the fixed force so replays of the same scenario are not identical.

# ref

"""

# import built in modules

# import custom packages

# ------------------------------------------------------------------------------

SCENARIOS = [
    {
        "sort_order": 1,
        "name": "Meeting Engagement",
        "year": 1944,
        "attacking_faction": "soviet",
        "defending_faction": "contested",
        "map_areas": "town,town",
        "german_random_points": 400,
        "soviet_random_points": 450,
        "german_squads": (
            "German 1944 Rifle:4,"
            "German 1944 Panzergrenadier Mech:2,"
            "German sMG42:1,"
            "German Panzer IV Ausf H:2,"
            "German Sd.kfz.222:1,"
            "German Medic:1,"
            "German FeldFunk Team:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:5,"
            "Soviet 1944 SMG:3,"
            "Soviet T34-76 Model 1943:2,"
            "Soviet T-70:1,"
            "Soviet BA-64:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "Summer 1944, somewhere west of the Dnieper. Neither side holds "
            "the ground. A German kampfgruppe and a Soviet forward detachment "
            "run into each other around two villages and a stretch of dirt "
            "road. Both forces are mixed and neither has a prepared defense. "
            "A small random attachment joins each side."
        ),
    },
    {
        "sort_order": 2,
        "name": "Hold the Village",
        "year": 1944,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "town,town,town",
        "german_random_points": 300,
        "soviet_random_points": 500,
        "german_squads": (
            "German 1944 Rifle:6,"
            "German 1944 Volksgrenadier Fire Group:2,"
            "German 1944 Volksgrenadier Storm Group:2,"
            "German sMG42:2,"
            "German PAK 40:2,"
            "German StuG III Ausf G:1,"
            "German 8 cm Mortar Team:1,"
            "German Medic:1,"
            "German FeldFunk Team:1,"
            "German Mechanic:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:8,"
            "Soviet 1944 SMG:4,"
            "Soviet 1943 Assault SMG:2,"
            "Soviet T34-76 Model 1943:3,"
            "Soviet 82 mm Mortar Team:2,"
            "Soviet PTRS-41 AT Squad:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "A German company has had one night to dig in around a cluster of "
            "villages. Pak 40s cover the approaches and a single StuG is the "
            "mobile reserve. At dawn a Soviet rifle battalion attacks with "
            "T-34s and mortars. The defenders must hold the towns. The "
            "attackers must take them before the rest of the division arrives."
        ),
    },
    {
        "sort_order": 3,
        "name": "Panzer Counterattack",
        "year": 1944,
        "attacking_faction": "german",
        "defending_faction": "soviet",
        "map_areas": "town,town",
        "german_random_points": 400,
        "soviet_random_points": 350,
        "german_squads": (
            "German Panzer IV Ausf H:3,"
            "German 1944 Panzergrenadier Mech:3,"
            "German 1944 Rifle:3,"
            "German Sd.kfz.251/9:1,"
            "German Sd.kfz.251/2:1,"
            "German PAK 40 with Sd.kfz.10:1,"
            "German Medic:1,"
            "German FeldFunk Team:1,"
            "German Mechanic:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:6,"
            "Soviet 1944 SMG:3,"
            "Soviet ZiS-3 76mm Divisional Gun:2,"
            "Soviet T34-76 Model 1943:2,"
            "Soviet PTRS-41 AT Squad:2,"
            "Soviet 82 mm Mortar Team:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "The Soviets took the town yesterday. This morning a German "
            "kampfgruppe of Panzer IVs and panzergrenadiers counterattacks "
            "to throw them back out. The Soviet defenders have a pair of "
            "ZiS-3s, a few T-34s, and infantry still reorganizing in the "
            "houses. Armor leads. Infantry has to keep up."
        ),
    },
    {
        "sort_order": 4,
        "name": "Tiger at the Crossroads",
        "year": 1944,
        "attacking_faction": "german",
        "defending_faction": "soviet",
        "map_areas": "town,town",
        "german_random_points": 250,
        "soviet_random_points": 500,
        "german_squads": (
            "German Panzer VI Ausf E:1,"
            "German Panzer IV Ausf H:1,"
            "German 1944 Rifle:4,"
            "German 1944 Panzergrenadier Mech:2,"
            "German sMG42:1,"
            "German Panzerschreck Team:1,"
            "German Medic:1,"
            "German FeldFunk Team:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:6,"
            "Soviet 1944 SMG:3,"
            "Soviet T34-76 Model 1943:2,"
            "Soviet SU-85:2,"
            "Soviet PTRS-41 AT Squad:2,"
            "Soviet ZiS-3 76mm Divisional Gun:3,"
            "Soviet Medic:1"
        ),
        "description": (
            "A Tiger I and a supporting Panzer IV are committed to seize a "
            "road junction held by Soviet infantry. Two SU-85s and a pair of "
            "T-34s are the Soviet answer to the heavy tank. Frontal shots on "
            "the Tiger will disappoint. Flank shots, AT rifles, and the SU-85s "
            "are the real threat. The Germans have very little else."
        ),
    },
    {
        "sort_order": 5,
        "name": "Bagration Breakthrough",
        "year": 1944,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "town,town,town",
        "german_random_points": 250,
        "soviet_random_points": 600,
        "german_squads": (
            "German 1944 Rifle:4,"
            "German 1944 Volksgrenadier Fire Group:2,"
            "German 1944 Volksgrenadier Storm Group:1,"
            "German sMG42:1,"
            "German PAK 40:2,"
            "German StuG III Ausf G:1,"
            "German Luftwaffe MG-15 Crew:1,"
            "German Medic:1,"
            "German FeldFunk Team:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:10,"
            "Soviet 1944 SMG:4,"
            "Soviet 1943 Assault SMG:3,"
            "Soviet T34-76 Model 1943:4,"
            "Soviet T-70:1,"
            "Soviet 82 mm Mortar Team:2,"
            "Soviet PTRS-41 AT Squad:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "June 1944. Army Group Centre is coming apart. A thin German "
            "line of riflemen, Volksgrenadiers, and two Pak 40s is all that "
            "covers three villages. A Soviet rifle regiment with T-34s is "
            "coming straight through. The defenders are outnumbered. The "
            "StuG is the only mobile fire brigade they have left."
        ),
    },
    {
        "sort_order": 6,
        "name": "The StuG Line",
        "year": 1944,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "town,town",
        "german_random_points": 300,
        "soviet_random_points": 450,
        "german_squads": (
            "German StuG III Ausf G:3,"
            "German PAK 40:2,"
            "German 1944 Rifle:5,"
            "German sMG42:2,"
            "German Panzerschreck Team:1,"
            "German Medic:1,"
            "German FeldFunk Team:1,"
            "German Mechanic:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:6,"
            "Soviet 1944 SMG:3,"
            "Soviet T34-76 Model 1943:4,"
            "Soviet SU-85:2,"
            "Soviet 82 mm Mortar Team:1,"
            "Soviet PTRS-41 AT Squad:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "Three StuG III Ausf G and a pair of Pak 40s form a gun line "
            "across two villages. Soviet tank riders and a company of T-34-76s "
            "have to break it. The assault guns are hull-down specialists. "
            "If the Soviets close the range or find a flank, the StuGs become "
            "short-ranged and slow to traverse."
        ),
    },
    {
        "sort_order": 7,
        "name": "Airfield",
        "year": 1944,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "airport,town",
        "german_random_points": 300,
        "soviet_random_points": 400,
        "german_squads": (
            "German 1944 Fallschirmjager:3,"
            "German 1944 Rifle:3,"
            "German Luftwaffe MG-15 Crew:2,"
            "German Sd.kfz.222:1,"
            "German Kubelwagen:2,"
            "German PAK 40:1,"
            "German StuG III Ausf G:1,"
            "German Medic:1,"
            "German FeldFunk Team:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle Motorized:4,"
            "Soviet 1944 SMG:3,"
            "Soviet 1944 Rifle:3,"
            "Soviet T-70:2,"
            "Soviet T34-76 Model 1943:1,"
            "Soviet BA-64:2,"
            "Soviet Zis 5 Truck:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "A Luftwaffe field on the edge of a town is about to be overrun. "
            "Fallschirmjager and a scratch rifle force are still on the "
            "perimeter. A Soviet motorized probe with T-70s and a single "
            "T-34 is rolling in from the east. Open ground around the strip "
            "favors the Pak and the StuG. The town is the only cover the "
            "attackers will get."
        ),
    },
    {
        "sort_order": 8,
        "name": "Recon Screen",
        "year": 1944,
        "attacking_faction": "soviet",
        "defending_faction": "none",
        "map_areas": "town",
        "german_random_points": 250,
        "soviet_random_points": 250,
        "german_squads": (
            "German Aufklaren Kubelwagen:2,"
            "German Sd.kfz.222:2,"
            "German Bike Messenger:2,"
            "German Bike AT Squad:1,"
            "German 1944 Rifle:2,"
            "German Kubelwagen:1"
        ),
        "soviet_squads": (
            "Soviet BA-64:2,"
            "Soviet 1944 Rifle Motorized:3,"
            "Soviet T-70:1,"
            "Soviet GAZ 61:1,"
            "Soviet Sniper Squad SVT-40:1"
        ),
        "description": (
            "Two recon screens collide around a single village. Light cars, "
            "armored cars, bikes, and a handful of infantry. Nobody has a "
            "prepared defense and nobody has a heavy tank. First side to "
            "hold the town wins the meeting. A small random attachment may "
            "include something heavier than either commander expected."
        ),
    },
    {
        "sort_order": 9,
        "name": "Elefant",
        "year": 1944,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "town,town",
        "german_random_points": 200,
        "soviet_random_points": 550,
        "german_squads": (
            "German Panzerjager Tiger P:1,"
            "German 1944 Rifle:5,"
            "German sMG42:1,"
            "German PAK 40:1,"
            "German Panzerschreck Team:1,"
            "German Medic:1,"
            "German FeldFunk Team:1,"
            "German Mechanic:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:6,"
            "Soviet 1944 SMG:4,"
            "Soviet T34-85:3,"
            "Soviet SU-85:2,"
            "Soviet T34-76 Model 1943:2,"
            "Soviet PTRS-41 AT Squad:2,"
            "Soviet 82 mm Mortar Team:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "One Elefant is hull-down covering two villages. The 88 will "
            "kill anything the Soviets drive at it from the front. Infantry "
            "has to keep the monster from being flanked, because once T-34s "
            "or SU-85s are in the side armor the fight is over. The Soviets "
            "have the numbers. They do not have a tank that wants a fair "
            "duel."
        ),
    },
    {
        "sort_order": 10,
        "name": "Hetzer Ambush",
        "year": 1945,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "town,town",
        "german_random_points": 300,
        "soviet_random_points": 450,
        "german_squads": (
            "German Hetzer Squad:2,"
            "German Panzer IV Ausf J:1,"
            "German 1944 Volksgrenadier Fire Group:3,"
            "German 1944 Volksgrenadier Storm Group:2,"
            "German 1945 PanzerJager:2,"
            "German PAK 40:1,"
            "German sMG42:1,"
            "German Medic:1,"
            "German FeldFunk Team:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Rifle:5,"
            "Soviet 1944 SMG:4,"
            "Soviet T34-85:4,"
            "Soviet SU-100:1,"
            "Soviet 82 mm Mortar Team:1,"
            "Soviet PTRS-41 AT Squad:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "Early 1945. Two Hetzers and a late Panzer IV wait in a pair of "
            "villages with Volksgrenadiers and Panzerjaeger infantry. A "
            "Soviet force of T-34-85s and a SU-100 is probing west. The "
            "Hetzers are small and mean from ambush. They are also cramped, "
            "thin-sided, and finished if the 85s get around them."
        ),
    },
    {
        "sort_order": 11,
        "name": "The Oder",
        "year": 1945,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "town,town,town",
        "german_random_points": 350,
        "soviet_random_points": 500,
        "german_squads": (
            "German 1944 Volksgrenadier Fire Group:3,"
            "German 1944 Volksgrenadier Storm Group:3,"
            "German 1945 PanzerJager:2,"
            "German 1944 Rifle:2,"
            "German Hetzer Squad:1,"
            "German Panzer IV Ausf J:1,"
            "German PAK 40:2,"
            "German sMG42:2,"
            "German 8 cm Mortar Team:1,"
            "German Medic:1,"
            "German FeldFunk Team:1"
        ),
        "soviet_squads": (
            "Soviet 1944 SMG:6,"
            "Soviet 1943 Assault SMG:3,"
            "Soviet 1944 Assault Engineers:2,"
            "Soviet 1944 Rifle:4,"
            "Soviet T34-85:3,"
            "Soviet SU-100:1,"
            "Soviet SU-85M:1,"
            "Soviet 82 mm Mortar Team:2,"
            "Soviet Medic:1"
        ),
        "description": (
            "Spring 1945 on the approaches to the Oder. Volksgrenadiers and "
            "Panzerjaeger teams hold a string of towns with a Hetzer and a "
            "Panzer IV J in support. Soviet assault groups - SMG, engineers, "
            "T-34-85s and a SU-100 - are coming in to clear the houses. "
            "Short range, lots of infantry, bad news for anyone still in "
            "the street."
        ),
    },
    {
        "sort_order": 12,
        "name": "Assault on the Town",
        "year": 1945,
        "attacking_faction": "soviet",
        "defending_faction": "german",
        "map_areas": "town,town,town",
        "german_random_points": 250,
        "soviet_random_points": 400,
        "german_squads": (
            "German 1944 Volksgrenadier Storm Group:4,"
            "German 1944 Volksgrenadier Fire Group:2,"
            "German 1945 PanzerJager:3,"
            "German sMG42:2,"
            "German Panzerschreck Team:2,"
            "German StuG III Ausf G:1,"
            "German Medic:1,"
            "German FeldFunk Team:1"
        ),
        "soviet_squads": (
            "Soviet 1944 Assault Engineers:3,"
            "Soviet 1943 Assault SMG:4,"
            "Soviet 1944 SMG:4,"
            "Soviet 1944 Rifle:3,"
            "Soviet T34-85:2,"
            "Soviet Sniper Squad SVT-40:1,"
            "Soviet 82 mm Mortar Team:1,"
            "Soviet Medic:1"
        ),
        "description": (
            "House-to-house. Soviet assault engineers and SMG groups attack "
            "a town held by Volksgrenadiers with panzerfausts and a single "
            "StuG. Armor is scarce and the streets are short. This is an "
            "infantry fight with a tank or two for moral support. The random "
            "attachment is small on purpose."
        ),
    },
]
