"""
repo : https://github.com/openmarmot/twe

notes :

static module with the following responsibilities
- build worlds
- load art assets (?)
- create world objects (can be called by anything)

the idea is this static class holds the standard way for creating objects
- anything that creates objects should do it here

Object definitions:
- Individual object definitions now live in code/engine/object_defs/
  (one .py per world_builder_identity string, organized in subfolders).
- They register themselves via @register_object from engine.object_registry.
- spawn_object() dispatches to the registry (all definitions now live in
  object_defs/ and register via @register_object).

# ref

"""

# import built in modules
import math
import random
import copy
import os
import sqlite3
import pkgutil
import importlib

# import custom packages
import engine.math_2d
import engine.name_gen
import engine.log
from engine.world_object import WorldObject
from engine.world_area import WorldArea
from engine.map_object import MapObject
import engine.penetration_calculator
from engine.vehicle_role import VehicleRole
import engine.map_generator
import engine.battlegroup_generator


# load AI
from ai.ai_human import AIHuman
from ai.ai_vehicle import AIVehicle
from ai.ai_gun import AIGun
from ai.ai_magazine import AIMagazine
from ai.ai_none import AINone
from ai.ai_building import AIBuilding
from ai.ai_projectile import AIProjectile
from ai.ai_throwable import AIThrowable
from ai.ai_squad import AISquad
from ai.ai_map_pointer import AIMapPointer
from ai.ai_container import AIContainer
from ai.ai_consumable import AIConsumable
from ai.ai_medical import AIMedical
from ai.ai_engine import AIEngine
from ai.ai_coffee_grinder import AICoffeeGrinder
from ai.ai_animated_sprite import AIAnimatedSprite
from ai.ai_wearable import AIWearable
from ai.ai_battery import AIBattery
from ai.ai_radio import AIRadio
from ai.ai_turret import AITurret
from ai.ai_rotor import AIRotor
from ai.ai_hit_marker import AIHitMarker
from ai.ai_dani import AIDani
from ai.ai_wheel import AIWheel
from ai.ai_optic import AIOptic

# object registry lives in a tiny separate module to avoid circular imports
# when object definition modules (which need to @register) are imported while
# world_builder itself is still being initialized.
from engine.object_registry import OBJECT_REGISTRY


def _load_object_definitions():
    """Discover and import every .py file under engine/object_defs (including subdirs).
    Uses filesystem walk. Files starting with '_' are skipped.
    Each module is expected to call @register_object at import time.
    """
    import os
    base_dir = os.path.join(os.path.dirname(__file__), "object_defs")
    base_import = "engine.object_defs"

    for root, dirs, files in os.walk(base_dir):
        for fname in files:
            if not fname.endswith(".py") or fname.startswith("_"):
                # skip files starting with _ (private files)
                continue
            # compute module path relative to base_dir
            rel_dir = os.path.relpath(root, base_dir)
            if rel_dir == ".":
                mod_tail = fname[:-3]
            else:
                mod_tail = rel_dir.replace(os.sep, ".") + "." + fname[:-3]
            full_mod = base_import + "." + mod_tail
            try:
                importlib.import_module(full_mod)
            except Exception as e:
                engine.log.add_data("error", f"Failed to load object def {full_mod}: {e}", True)


# global variables

# ------ object rarity lists -----------------------------------
list_consumables = [
    "green_apple",
    "potato",
    "turnip",
    "cucumber",
    "pickle",
    "adler-cheese",
    "spam",
    "german_field_rations",
    "soviet_field_rations",
    "german_white_beans",
    "soviet_white_beans",
    "german_herrings",
    "soviet_herrings",
    "german_schmalzfleisch",
    "german_rinderbraten",
    "german_chicken",
    "german_sardinen",
    "german_linsen",
    "german_erbsensuppe",
    "german_gulaschsuppe",
    "german_tomatencremesuppe",
    "soviet_corned_beef",
    "soviet_beef_stew",
    "soviet_chicken",
    "soviet_sardines",
    "soviet_solyanka",
    "soviet_borscht",
    "camembert-cheese",
    "champignon-cheese",
    "karwendel-cheese",
    "wine",
    "schokakola",
    "coffee",
    "schnaps",
    "kvass",
    "canned_peas",
    "canned_carrots",
    "sauerkraut",
]
list_consumables_common = ["green_apple", "potato", "turnip", "cucumber", "pickle", "german_field_rations", "soviet_field_rations", "german_white_beans", "soviet_white_beans", "german_herrings", "soviet_herrings", "kvass", "canned_peas", "canned_carrots", "sauerkraut"]
list_consumables_rare = [
    "adler-cheese",
    "german_schmalzfleisch",
    "german_rinderbraten",
    "german_chicken",
    "german_sardinen",
    "german_linsen",
    "german_erbsensuppe",
    "german_gulaschsuppe",
    "german_tomatencremesuppe",
    "soviet_corned_beef",
    "soviet_beef_stew",
    "soviet_chicken",
    "soviet_sardines",
    "soviet_solyanka",
    "soviet_borscht",
    "camembert-cheese",
    "champignon-cheese",
    "karwendel-cheese",
    "wine",
    "beer",
    "vodka",
    "coffee",
    "schnaps",
    "kvass",
    "canned_peas",
    "canned_carrots",
    "sauerkraut",
]
list_consumables_ultra_rare = ["schokakola", "spam"]

list_household_items = ["blue_coffee_cup", "coffee_tin", "coffee_grinder", "pickle_jar"]

list_guns = [
    "kar98k",
    "stg44",
    "mp40",
    "mg34",
    "mg42",
    "mosin_nagant",
    "ppsh43",
    "ppsh41",
    "dp28",
    "1911",
    "ppk",
    "tt33",
    "g41w",
    "k43",
    "svt40",
    "svt40-sniper",
    "mg15",
    "fg42-type1",
    "fg42-type2",
    "c96",
    "c96_red_9",
]
list_guns_common = ["kar98k", "mosin_nagant", "ppsh43", "ppsh41", "tt33", "svt40"]
list_guns_rare = ["mp40", "ppk", "stg44", "mg34", "dp28", "k43", "g41w", "c96"]
list_guns_ultra_rare = [
    "fg42-type1",
    "fg42-type2",
    "svt40-sniper",
    "1911",
    "mg15",
    "c96_red_9",
]
list_german_guns = [
    "kar98k",
    "stg44",
    "mp40",
    "mg34",
    "ppk",
    "k43",
    "g41w",
    "fg42-type1",
    "fg42-type2",
    "walther_p38",
]

list_guns_rifles = ["kar98k", "mosin_nagant", "g41w", "k43", "svt40", "svt40-sniper"]
list_guns_smg = ["mp40", "ppsh43", "ppsh41"]
list_guns_assault_rifles = ["stg44"]
list_guns_machine_guns = ["mg34", "mg42", "dp28", "mg15", "fg42-type1", "fg42-type2"]
list_guns_pistols = [
    "1911",
    "ppk",
    "tt33",
    "c96",
    "c96_red_9",
    "walther_p38",
    "luger_p08",
]
list_guns_at_rifles = ["ptrs_41"]

list_german_military_equipment = ["german_folding_shovel", "german_field_shovel"]


list_medical = ["bandage", "german_officer_first_aid_kit"]
list_medical_common = ["bandage"]
list_medical_rare = ["german_officer_first_aid_kit"]
list_medical_ultra_rare = []
# ----------------------------------------------------------------

# ------ variables that get pulled from sqlite -----------------------------------
squad_data = {}


# ------------------------------------------------------------------------------
def add_random_pistol_to_inventory(wo, world):
    """adds a random pistol to the inventory"""

    pistol_type = random.choice(list_guns_pistols)
    pistol = spawn_object(world, wo.world_coords, pistol_type, False)
    wo.add_inventory(pistol)
    magazine_type = pistol.ai.magazine.world_builder_identity
    for _ in range(2):
        wo.add_inventory(spawn_object(world, wo.world_coords, magazine_type, False))


# ------------------------------------------------------------------------------
def add_standard_loadout(wo, world, loadout):
    """adds a standard loadout to the world object"""
    # loadout - list of strings that correspond to the loadout
    # returns the world object with the loadout added

    if loadout == "dp28":
        wo.add_inventory(spawn_object(world, [0, 0], "dp28", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "dp28_magazine", False))
    elif loadout == "fg42-type2":
        wo.add_inventory(spawn_object(world, [0, 0], "fg42-type2", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "fg42_type2_magazine", False))
    elif loadout == "g41w":
        wo.add_inventory(spawn_object(world, [0, 0], "g41w", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "g41w_magazine", False))
    elif loadout == "kar98k":
        wo.add_inventory(spawn_object(world, [0, 0], "kar98k", False))
        for _ in range(12):
            wo.add_inventory(spawn_object(world, [0, 0], "kar98k_magazine", False))
    elif loadout == "kar98k_schiessbecher":
        wo.add_inventory(spawn_object(world, [0, 0], "kar98k_schiessbecher", False))
        for _ in range(12):
            wo.add_inventory(spawn_object(world, [0, 0], "kar98k_magazine", False))

        # this is likely excessive but it represents squad mates carrying grenades
        for _ in range(6):
            wo.add_inventory(
                spawn_object(world, [0, 0], "schiessbecher_grenade", False)
            )
        for _ in range(6):
            wo.add_inventory(
                spawn_object(world, [0, 0], "schiessbecher_grenade_heat", False)
            )

    elif loadout == "k43":
        wo.add_inventory(spawn_object(world, [0, 0], "k43", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "k43_magazine", False))
    elif loadout == "mg15":
        wo.add_inventory(spawn_object(world, [0, 0], "mg15", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "mg15_drum_magazine", False))
    elif loadout == "mg34":
        wo.add_inventory(spawn_object(world, [0, 0], "mg34", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "mg34_drum_magazine", False))
    elif loadout == "mg42":
        wo.add_inventory(spawn_object(world, [0, 0], "mg42", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "mg34_drum_magazine", False))
    elif loadout == "mosin_nagant":
        wo.add_inventory(spawn_object(world, [0, 0], "mosin_nagant", False))
        for _ in range(12):
            wo.add_inventory(spawn_object(world, [0, 0], "mosin_magazine", False))
    elif loadout == "mp40":
        wo.add_inventory(spawn_object(world, [0, 0], "mp40", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "mp40_magazine", False))
    elif loadout == "panzerschreck":
        wo.add_inventory(spawn_object(world, [0, 0], "panzerschreck", False))
        for _ in range(6):
            wo.add_inventory(
                spawn_object(world, [0, 0], "panzerschreck_magazine", False)
            )
    elif loadout == "ppsh43":
        wo.add_inventory(spawn_object(world, [0, 0], "ppsh43", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "ppsh43_magazine", False))
    elif loadout == "ppsh41":
        wo.add_inventory(spawn_object(world, [0, 0], "ppsh41", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "ppsh41_box_magazine", False))
    elif loadout == "ptrs_41":
        wo.add_inventory(spawn_object(world, [0, 0], "ptrs_41", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "ptrs_41_magazine", False))
    elif loadout == "standard_german_gear":
        wo.add_inventory(spawn_object(world, [0, 0], "helmet_stahlhelm", False))
        wo.add_inventory(spawn_object(world, [0, 0], "model24", False))
        wo.add_inventory(spawn_object(world, [0, 0], "bandage", False))
        wo.ai.wallet["German Military Script"] = round(random.uniform(0.05, 1.5), 2)
    elif loadout == "standard_soviet_gear":
        wo.add_inventory(spawn_object(world, [0, 0], "helmet_ssh40", False))
        wo.add_inventory(spawn_object(world, [0, 0], "rg_42_grenade", False))
        wo.add_inventory(spawn_object(world, [0, 0], "bandage", False))
        wo.ai.wallet["Soviet Ruble"] = round(random.uniform(0.05, 1.5), 2)
    elif loadout == "stg44":
        wo.add_inventory(spawn_object(world, [0, 0], "stg44", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "stg44_magazine", False))
    elif loadout == "svt40":
        wo.add_inventory(spawn_object(world, [0, 0], "svt40", False))
        for _ in range(6):
            wo.add_inventory(spawn_object(world, [0, 0], "svt40_magazine", False))
    elif loadout == "tt33":
        wo.add_inventory(spawn_object(world, [0, 0], "tt33", False))
        for _ in range(2):
            wo.add_inventory(spawn_object(world, [0, 0], "tt33_magazine", False))
    elif loadout == "walther_p38":
        wo.add_inventory(spawn_object(world, [0, 0], "walther_p38", False))
        for _ in range(2):
            wo.add_inventory(spawn_object(world, [0, 0], "p38_magazine", False))
    elif loadout == "luger_p08":
        wo.add_inventory(spawn_object(world, [0, 0], "luger_p08", False))
        for _ in range(2):
            wo.add_inventory(spawn_object(world, [0, 0], "luger_p08_magazine", False))


# ------------------------------------------------------------------------------
def convert_map_objects_to_world_objects(world, map_objects):
    """handles converting map_objects to world_objects and spawns them"""

    # note - unsure whether it is best to spawn the objects at this time or not.
    # for now i'm going to spawn them here

    for map_object in map_objects:
        # world_area_ is a special case object
        if map_object.world_builder_identity.startswith("world_area"):
            # make the corresponding WorldArea object
            w = WorldArea(world)
            w.world_coords = map_object.world_coords
            w.name = map_object.name
            w.area_type = map_object.world_builder_identity.split("world_area_")[1]

            # register with world
            world.world_areas.append(w)
        else:
            wo = spawn_object(
                world, map_object.world_coords, map_object.world_builder_identity, True
            )

            if wo is None:
                # this means the world_builder_identity was not recognized by spawn_object
                engine.log.add_data(
                    "error",
                    "world_builder.convert_map_objects_to_world_objects could not convert "
                    + map_object.world_builder_identity,
                    True,
                )
            else:
                wo.rotation_angle = map_object.rotation

                if map_object.name not in ("none", ""):
                    wo.name = map_object.name

                # add in the saved inventory
                # remember that map_object.inventory is a array of world_builder_identity names
                if len(map_object.inventory) > 0:
                    # print('inventory',map_object.inventory)
                    # need to prevent duplicates. this could be better
                    for a in map_object.inventory:
                        already_exists = False
                        for b in wo.ai.inventory:
                            if b.world_builder_identity == a:
                                already_exists = True
                                break
                        if already_exists is False:
                            wo.ai.inventory.append(
                                spawn_object(world, [0, 0], a, False)
                            )

    # this is needed to flush all the new objects out of the queue and into the world
    world.process_add_remove_queue()


# ------------------------------------------------------------------------------
def convert_world_objects_to_map_objects(world, map_square):
    """converts all world objects to map objects"""

    # clear old map objects
    map_square.map_objects = []

    # convert world areas to map objects
    for b in world.world_areas:
        # we don't save the dynamic ones, they are generated each time
        if b.area_type != "dynamic":
            temp = MapObject("world_area_" + b.area_type, b.name, b.world_coords, 0, [])
            map_square.map_objects.append(temp)

    # convert world objects to map objects
    for b in world.grid_manager.get_all_objects():
        # a couple objects we don't want to save
        if b.no_save is False:
            # assemble inventory name list
            inventory = []
            if hasattr(b.ai, "inventory"):
                for i in b.ai.inventory:
                    inventory.append(i.world_builder_identity)
            temp = MapObject(
                b.world_builder_identity, b.name, b.world_coords, 0, inventory
            )
            map_square.map_objects.append(temp)

    # TBD - handle objects that exited the map


# ------------------------------------------------------------------------------
def fill_container(world, container, fill_name):
    """fill container with an object (liquid)"""
    # CONTAINER - should be empty
    # FILL_NAME - name of object (liquid) to fill the container with

    fill = spawn_object(world, [0, 0], fill_name, False)
    fill.volume = container.volume
    # need something more clever here.. maybe a density value per object
    fill.weight = container.volume
    container.ai.inventory.append(fill)


# ------------------------------------------------------------------------------
def generate_dynamic_world_areas(world):
    """generates dynamic world areas"""
    # create some world areas after the world loaded
    # combat ai needs arount 5 or so world_areas to be interesting

    # first some directional ones

    w = WorldArea(world)
    w.world_coords = [-5000, 0]
    w.name = "west"
    w.area_type = "dynamic"
    world.world_areas.append(w)

    w = WorldArea(world)
    w.world_coords = [5000, 0]
    w.name = "east"
    w.area_type = "dynamic"
    world.world_areas.append(w)

    w = WorldArea(world)
    w.world_coords = [0, -5000]
    w.name = "north"
    w.area_type = "dynamic"
    world.world_areas.append(w)

    w = WorldArea(world)
    w.world_coords = [0, 5000]
    w.name = "south"
    w.area_type = "dynamic"
    world.world_areas.append(w)


# ------------------------------------------------------------------------------
def get_random_from_list(world, world_coords, OBJECT_LIST, spawn):
    """returns a random object from a list"""
    # OBJECT_LIST : a list of strings that correspond to an object_Type for the
    # spawn_object function
    index = random.randint(0, len(OBJECT_LIST) - 1)
    return spawn_object(world, world_coords, OBJECT_LIST[index], spawn)


# ------------------------------------------------------------------------------
# map object world_coords marker for reinforcement units (main force uses [0, 0]).
# create_squads reads this before positions are reassigned.
REINFORCEMENT_MAP_COORDS = [1, 0]


def get_squad_map_objects(squad_name, world_coords=None):
    """get a list of map objects that make up a squad"""
    # world_coords - optional spawn marker. default [0, 0] for main force.
    # use REINFORCEMENT_MAP_COORDS for reinforcement units.
    if world_coords is None:
        world_coords = [0, 0]

    global squad_data
    members = []
    if squad_name in squad_data:
        members = [m.strip() for m in squad_data[squad_name]["members"].split(",")]

    else:
        print("squad data", squad_data)
        engine.log.add_data(
            "error",
            "worldbuilder.get_squad_map_objects squad_name "
            + squad_name
            + " not recognized",
            True,
        )

    # convert each member to a map_object
    map_objects = []
    for b in members:
        map_objects.append(MapObject(b, "none", list(world_coords), 0, []))

    return map_objects


# ------------------------------------------------------------------------------
def load_magazine(world, magazine, projectile_type=None, tracers=False):
    """loads a magazine with bullets"""
    # wipe whatever is in there
    magazine.ai.projectiles = []

    # gives the option to specify the projectile to load
    if projectile_type == None:
        projectile_type = magazine.ai.compatible_projectiles[0]

    if projectile_type in magazine.ai.compatible_projectiles:
        count = len(magazine.ai.projectiles)
        tracer_interval = 5
        projectile_count = 0
        while count < magazine.ai.capacity:
            projectile_count += 1
            z = spawn_object(world, [0, 0], "projectile", False)
            z.ai.projectile_type = projectile_type

            # change to a bigger projectile image. might make a couple more
            if (
                engine.penetration_calculator.projectile_data[projectile_type][
                    "diameter"
                ]
                > 14
            ):
                z.image_list = ["projectile_mid"]

            if tracers and projectile_count % tracer_interval == 0:
                z.image_list = ["tracer_green"]
            magazine.ai.projectiles.append(z)

            count += 1
    else:
        engine.log.add_data(
            "Error",
            "world_builder.load_magazine incompatible projectile type: "
            + projectile_type,
            True,
        )

    # set use case. first reset defaults as this function can be called multiple times
    magazine.ai.use_antitank = False
    magazine.ai.use_antipersonnel = False
    if engine.penetration_calculator.projectile_data[projectile_type]["use"] == "at":
        magazine.ai.use_antitank = True
    elif engine.penetration_calculator.projectile_data[projectile_type]["use"] == "ap":
        magazine.ai.use_antipersonnel = True
    elif (
        engine.penetration_calculator.projectile_data[projectile_type]["use"] == "both"
    ):
        magazine.ai.use_antipersonnel = True
        magazine.ai.use_antitank = True
    else:
        engine.log.add_data(
            "Error",
            "world_builder.load_magazine unknown use for projectile: "
            + projectile_type,
            True,
        )


# ------------------------------------------------------------------------------
def load_quick_battle_map_objects(battle_option, result_container):
    """load quick battle map objects. called by game menu"""

    # this is called in a thread by graphics_2d_pygame.load_quick_battle
    # normalize - game menu passes string keys; --ai-test / --quick-battle pass ints
    battle_option = str(battle_option)

    world_area_options = []
    world_area_options.append(["town", "town", "town"])
    world_area_options.append(["airport", "town"])
    map_areas = random.choice(world_area_options)

    map_objects = engine.map_generator.generate_map(map_areas)

    year = random.choice([1944, 1945])

    # -- initial troops --
    squads = []
    reinforcement_squads = []
    points = 0
    soviet_advantage = 0

    if battle_option == "1":
        points = 2500
        soviet_advantage = points * 0.3
        print(f"soviet advantage: {soviet_advantage}")
        squads += engine.battlegroup_generator.create_random_battlegroup(
            "german", points, squad_data, year
        )
        squads += engine.battlegroup_generator.create_random_battlegroup(
            "soviet", points + soviet_advantage, squad_data, year
        )

    elif battle_option == "2":
        points = 5000
        soviet_advantage = points * 0.3
        print(f"soviet advantage: {soviet_advantage}")
        squads += engine.battlegroup_generator.create_random_battlegroup(
            "german", points, squad_data, year
        )
        squads += engine.battlegroup_generator.create_random_battlegroup(
            "soviet", points + soviet_advantage, squad_data, year
        )
        # squads.append('German Panzerjager Tiger P camo1')
        # squads.append('Soviet SU-85')
        # squads.append('Soviet SU-85')
        # squads.append('Soviet SU-85')

    elif battle_option == "3":
        points = 10000
        soviet_advantage = points * 0.3
        print(f"soviet advantage: {soviet_advantage}")
        squads += engine.battlegroup_generator.create_random_battlegroup(
            "german", points, squad_data, year
        )
        squads += engine.battlegroup_generator.create_random_battlegroup(
            "soviet", points + soviet_advantage, squad_data, year
        )

    # testing
    elif battle_option == "4":

        for s in range(20):
            squads.append("Soviet T-70")
            squads.append("Soviet 1944 Rifle")
            squads.append("Soviet 1944 Rifle Motorized")

            squads.append("German Sd.kfz.251/9")
            squads.append("German Sd.kfz.251/2")
            squads.append("German 1944 Rifle")

        # squads.append('Soviet T34-76 Model 1943')

        # squads.append('German Sd.kfz.251/9')

    # bench mark
    elif battle_option == "5":
        for b in range(100):
            squads.append("Soviet T34-76 Model 1943")
            squads.append("German Panzer IV Ausf G")

    # -- reinforcements (10% of main force points, battle options 1-3) --
    if points > 0:
        rein_points = int(points * 0.1)
        rein_soviet_advantage = soviet_advantage * 0.1
        print(f"reinforcement points: {rein_points}")
        reinforcement_squads += engine.battlegroup_generator.create_random_battlegroup(
            "german", rein_points, squad_data, year
        )
        reinforcement_squads += engine.battlegroup_generator.create_random_battlegroup(
            "soviet", rein_points + rein_soviet_advantage, squad_data, year
        )

    # convert squads to map objects
    # main force: [0, 0]. reinforcements: REINFORCEMENT_MAP_COORDS marker for create_squads
    for squad in squads:
        map_objects += get_squad_map_objects(squad)
    for squad in reinforcement_squads:
        map_objects += get_squad_map_objects(squad, REINFORCEMENT_MAP_COORDS)

    # print squad summary table
    squad_counts = {}
    for s in squads:
        squad_counts[s] = squad_counts.get(s, 0) + 1
    rein_squad_counts = {}
    for s in reinforcement_squads:
        rein_squad_counts[s] = rein_squad_counts.get(s, 0) + 1
    print("=" * 50)
    print("=" * 50)
    engine.log.add_data("note", f"Quick battle year: {year}", True)
    print("\nSquad Summary:")
    print(f"{'Count':>5}  {'Squad Name'}")
    print("-" * 50)
    for name, count in sorted(squad_counts.items(), key=lambda x: (x[0], -x[1])):
        print(f"{count:>5}  {name}")
    if rein_squad_counts:
        print("\nReinforcement Squad Summary:")
        print(f"{'Count':>5}  {'Squad Name'}")
        print("-" * 50)
        for name, count in sorted(
            rein_squad_counts.items(), key=lambda x: (x[0], -x[1])
        ):
            print(f"{count:>5}  {name}")
    print()
    print("=" * 50)
    print("=" * 50)
    print()

    result_container[0] = map_objects


# ------------------------------------------------------------------------------
def load_sqlite_squad_data():
    """builds a squad_data dictionary from sqlite data"""
    global squad_data
    squad_data = {}

    conn = sqlite3.connect("data/data.sqlite")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM squad_data")

    # Fetch all column names
    column_names = [description[0] for description in cursor.description]
    # Fetch all rows from the table
    rows = cursor.fetchall()

    # Convert rows to dictionary, excluding the 'id' field
    for row in rows:
        row_dict = {
            column_names[i]: row[i]
            for i in range(len(column_names))
            if column_names[i] != "id"
        }
        key = row_dict.pop("name")
        squad_data[key] = row_dict

    # Close the database connection
    conn.close()


# ------------------------------------------------------------------------------
def load_world(world, map_objects, defending_faction):
    """coverts map_objects to world_objects and does everything necessary to load the world"""

    # this is called in a thread by graphics_2d_pygame.load_world()

    # convert map_objects to world_objects
    # note - this also spawns them and creates the world_area objects
    convert_map_objects_to_world_objects(world, map_objects)

    # this should be done before we create the dynamic areas as they are not interesting
    available_areas = world.world_areas[:]
    print(
        f"available areas count {len(available_areas)}, defending faction: {defending_faction}"
    )
    if available_areas and defending_faction in ["german", "soviet", "american"]:
        engine.log.add_data("note", f"{defending_faction} is defending.", True)
        world.tactical_ai[
            defending_faction
        ].initial_controlled_world_areas = available_areas

    if defending_faction == "mixed":
        print("mixed defending faction not implemented")

    # generate some minor world areas for battle flow
    generate_dynamic_world_areas(world)

    # perform all world start tasks
    world.start()


# ------------------------------------------------------------------------------
def spawn_aligned_pile(
    world, point_a, point_b, spawn_string, separation_distance, count, second_layer=True
):
    """spawn an aligned pile like a wood pile"""
    # point_a - initial spawn point
    # point_b - direction in which the pile grows to
    # spawn_string - name of the object to spawn
    # separation_distance - distance betwween objects

    rotation = engine.math_2d.get_rotation(point_a, point_b)
    heading = engine.math_2d.get_heading_from_rotation(rotation)

    # bottom layer
    current_coords = point_a
    for x in range(count):
        current_coords = engine.math_2d.moveAlongVector(
            separation_distance, current_coords, heading, 1
        )

        x = spawn_object(world, current_coords, spawn_string, True)
        x.rotation_angle = rotation
        x.heading = heading

    if second_layer:
        current_coords = engine.math_2d.moveAlongVector(
            separation_distance / 3, point_a, heading, 1
        )
        for x in range(int(count / 2)):
            current_coords = engine.math_2d.moveAlongVector(
                separation_distance, current_coords, heading, 1
            )

            x = spawn_object(world, current_coords, spawn_string, True)
            x.rotation_angle = rotation
            x.heading = heading


# ------------------------------------------------------------------------------
def spawn_container_body(name, world_object, image_index):
    """spawns a custom container for a body"""
    # name
    # world_object - the world_object that is being replaced
    # image_index - index of the image to be used - from the world object
    z = WorldObject(
        world_object.world, [world_object.image_list[image_index]], AIContainer
    )
    z.is_container = True
    z.name = name
    z.world_coords = world_object.world_coords
    z.rotation_angle = world_object.rotation_angle
    z.ai.inventory = world_object.ai.inventory.copy()
    z.world_builder_identity = "body"
    z.volume = world_object.volume
    z.weight = world_object.weight
    z.collision_radius = world_object.collision_radius
    z.is_large_human_pickup = True
    z.is_body = True
    # containers normally update to handle leaks - this is no update for performance considerations
    z.no_update = True
    z.wo_start()


# ------------------------------------------------------------------------------
def spawn_drop_canister(world, world_coords, CRATE_TYPE):
    """generates different crate types with contents"""

    z = spawn_object(world, world_coords, "german_drop_canister", True)

    if CRATE_TYPE == "mixed_supply":
        z.ai.inventory.append(
            get_random_from_list(world, world_coords, list_german_guns, False)
        )
        z.ai.inventory.append(
            get_random_from_list(world, world_coords, list_german_guns, False)
        )
        z.ai.inventory.append(
            spawn_object(world, world_coords, "panzerfaust_60", False)
        )
        z.ai.inventory.append(
            spawn_object(world, world_coords, "panzerfaust_100", False)
        )
        z.ai.inventory.append(
            get_random_from_list(world, world_coords, list_consumables_common, False)
        )
        z.ai.inventory.append(
            get_random_from_list(world, world_coords, list_consumables_common, False)
        )
        z.ai.inventory.append(
            get_random_from_list(world, world_coords, list_medical, False)
        )
        z.ai.inventory.append(
            get_random_from_list(world, world_coords, list_medical, False)
        )


# ------------------------------------------------------------------------------
def spawn_explosion_and_fire(world, world_coords, fire_duration, smoke_duration):
    """spawn explosion and fire effects"""
    heading = [0, 0]

    for x in range(10):
        coords = [
            world_coords[0] + random.randint(-2, 2),
            world_coords[1] + random.randint(-2, 2),
        ]
        z = spawn_object(world, coords, "small_smoke", True)
        z.heading = heading
        z.ai.speed = random.uniform(1, 2)
        z.ai.rotation_speed = random.randint(30, 40)
        z.ai.rotate_time_max = 60
        z.ai.move_time_max = 3
        z.ai.alive_time_max = smoke_duration

    for x in range(1):
        coords = [
            world_coords[0] + random.randint(-2, 2),
            world_coords[1] + random.randint(-2, 2),
        ]
        z = spawn_object(world, coords, "small_fire", True)
        z.heading = heading
        z.ai.speed = random.uniform(1, 2)
        z.ai.rotation_speed = random.randint(80, 90)
        z.ai.rotate_time_max = 5
        z.ai.move_time_max = 5
        z.ai.alive_time_max = fire_duration

    for x in range(5):
        coords = [
            world_coords[0] + random.randint(-2, 2),
            world_coords[1] + random.randint(-2, 2),
        ]
        z = spawn_object(world, coords, "small_flash", True)
        z.heading = heading
        z.ai.speed = random.uniform(1, 2)
        z.ai.rotation_speed = random.randint(400, 500)
        z.ai.rotate_time_max = 1.8
        z.ai.move_time_max = 3
        z.ai.alive_time_max = random.uniform(0.1, 0.4)

    for x in range(1):
        coords = [
            world_coords[0] + random.randint(-2, 2),
            world_coords[1] + random.randint(-2, 2),
        ]
        z = spawn_object(world, coords, "small_explosion", True)
        z.heading = heading
        z.ai.speed = random.uniform(1, 2)
        z.ai.rotation_speed = random.randint(400, 500)
        z.ai.rotate_time_max = 1.8
        z.ai.move_time_max = 3
        z.ai.alive_time_max = random.uniform(0.09, 0.1)


# ------------------------------------------------------------------------------
def spawn_flash(world, world_coords, heading, amount=2):
    """spawn flash cloud"""

    for x in range(amount):
        coords = [
            world_coords[0] + random.randint(-2, 2),
            world_coords[1] + random.randint(-2, 2),
        ]
        z = spawn_object(world, coords, "small_flash", True)
        z.heading = heading
        z.ai.speed = random.uniform(1, 2)
        z.ai.rotation_speed = random.randint(400, 500)
        z.ai.rotate_time_max = 1.8
        z.ai.move_time_max = 3
        z.ai.alive_time_max = random.uniform(0.1, 0.4)


# ------------------------------------------------------------------------------
def spawn_object(world, world_coords, object_type, spawn):
    """returns new object. optionally spawns it in the world"""
    original_type = object_type
    z = None
    if object_type in OBJECT_REGISTRY:
        z = OBJECT_REGISTRY[object_type](world, world_coords)
    if z is not None:
        # registry-provided object: poison the type var so the legacy fallback
        # below does not execute (and to avoid treating None as an error).
        object_type = None  # poison value that matches nothing
    if object_type is not None:
        print("!! Spawn Error: " + object_type + " is not recognized.")

    # -- generic settings that apply to all --
    if z is None:
        return None
    z.world_builder_identity = original_type
    # set world coords if they weren't already set
    if z.world_coords == [0, 0]:
        z.world_coords = copy.copy(world_coords)

    # reset render level now that variables are set
    z.reset_render_level()
    if spawn:
        z.wo_start()
    return z


# ------------------------------------------------------------------------------
def spawn_map_pointer(world, TARGET_COORDS, TYPE):
    if TYPE == "normal":
        z = WorldObject(world, ["map_pointer_green"], AIMapPointer)
        z.ai.target_coords = TARGET_COORDS
        z.render_level = 4
        z.is_map_pointer = True
        z.wo_start()
    if TYPE == "blue":
        z = WorldObject(world, ["map_pointer_blue"], AIMapPointer)
        z.ai.target_coords = TARGET_COORDS
        z.render_level = 4
        z.is_map_pointer = True
        z.wo_start()
    if TYPE == "orange":
        z = WorldObject(world, ["map_pointer_orange"], AIMapPointer)
        z.ai.target_coords = TARGET_COORDS
        z.render_level = 4
        z.is_map_pointer = True
        z.wo_start()


# ------------------------------------------------------------------------------
# basically just a different kind of projectile
def spawn_shrapnel(
    world,
    world_coords,
    target_coords,
    ignore_list,
    projectile_type,
    min_time,
    max_time,
    originator,
    weapon,
):
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # MOUSE_AIM bool as to whether to use mouse aim for calculations
    z = WorldObject(world, ["shrapnel"], AIProjectile)
    z.name = "shrapnel"
    z.world_coords = copy.copy(world_coords)
    z.ai.starting_coords = copy.copy(world_coords)
    z.ai.speed = 300.0
    z.ai.maxTime = random.uniform(min_time, max_time)
    z.is_projectile = True
    z.render_level = 3
    z.ai.ignore_list = copy.copy(ignore_list)
    z.ai.projectile_type = projectile_type
    z.rotation_angle = engine.math_2d.get_rotation(world_coords, target_coords)
    z.heading = engine.math_2d.get_heading_vector(world_coords, target_coords)
    # increase the collision radius to make sure we get hits
    z.collision_radius = 10
    z.ai.shooter = originator
    z.ai.weapon = weapon
    z.wo_start()


# ------------------------------------------------------------------------------
def spawn_shrapnel_cloud(world, world_coords, amount, originator, weapon):
    """creates a shrapnel starburst pattern. used for grenades"""
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    ignore_list = []
    if world.friendly_fire_explosive is False:
        if originator.is_human:
            ignore_list += originator.ai.squad.faction_tactical.allied_humans

    elif world.friendly_fire_explosive_squad is False:
        if originator.is_human:
            # just add the squad
            ignore_list += originator.ai.squad.members

    for x in range(amount):
        target_coords = [
            float(random.randint(-150, 150)) + world_coords[0],
            float(random.randint(-150, 150)) + world_coords[1],
        ]
        spawn_shrapnel(
            world,
            world_coords,
            target_coords,
            ignore_list,
            "shrapnel",
            0.1,
            0.4,
            originator,
            weapon,
        )


# ------------------------------------------------------------------------------
def spawn_smoke_cloud(world, world_coords, heading, amount=30):
    """spawn smoke cloud"""
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel

    for x in range(amount):
        coords = [
            world_coords[0] + random.randint(-2, 2),
            world_coords[1] + random.randint(-2, 2),
        ]
        z = spawn_object(world, coords, "small_smoke", True)
        z.heading = heading
        z.ai.speed = random.uniform(5, 7)
        z.ai.rotation_speed = random.randint(400, 500)
        z.ai.rotate_time_max = 1.8
        z.ai.move_time_max = 3
        z.ai.alive_time_max = random.uniform(2.5, 3)


# ------------------------------------------------------------------------------
def spawn_sparks(world, world_coords, amount=30):
    """spawn spark"""
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel

    for x in range(amount):
        coords = [
            world_coords[0] + random.randint(-2, 2),
            world_coords[1] + random.randint(-2, 2),
        ]
        z = spawn_object(world, coords, "spark", True)
        z.heading = engine.math_2d.get_heading_from_rotation(z.rotation_angle)
        z.ai.speed = random.uniform(110, 130)
        z.ai.rotation_speed = 0
        z.ai.rotate_time_max = 0
        z.ai.move_time_max = 0.91
        z.ai.alive_time_max = random.uniform(1.1, 1.3)


# ------------------------------------------------------------------------------
def spawn_heat_jet(
    world, world_coords, target_coords, AMOUNT, heat_projectile_type, originator, weapon
):
    """creates a cone/line of shrapnel. used for panzerfaust"""
    # ORIGINATOR - the world object (human?) that is ultimately responsible for throwing/shooting the object that created the shrapnel
    # heat_projectile_type - a heat name from the projectile database that corresponds to the correct heat jet for the weapon
    for x in range(AMOUNT):
        target_coords = [
            float(random.randint(-5, 5)) + target_coords[0],
            float(random.randint(-5, 5)) + target_coords[1],
        ]
        spawn_shrapnel(
            world,
            world_coords,
            target_coords,
            [],
            heat_projectile_type,
            0.1,
            0.3,
            originator,
            weapon,
        )


# load squad data
load_sqlite_squad_data()

# populate the new per-file object registry (supports subfolders under object_defs/)
_load_object_definitions()
