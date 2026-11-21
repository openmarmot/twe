"""
mg151 drilling object definition

repo : https://github.com/openmarmot/twe

notes :
The Luftwaffe MG 151 Drilling. Three guns on one pedestal, one trigger.
fire_mode is simultaneous: every cycle fires every gun that still has a belt.
Set fire_mode to "sequential" and rate_of_fire to barrel_rate / 3 for a
staggered stream at the same combined rate.
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun_multi import AIGunMulti
import engine.world_builder
from engine.object_registry import register_object


def _create(world, world_coords, gun_id, name, description):
    z = WorldObject(world, ["mg34"], AIGunMulti)
    z.name = name
    z.description = description
    z.no_update = True
    z.minimum_visible_scale = 0.4
    z.is_gun = True
    # one salvo per gun cycle. each barrel keeps its own cyclic limit.
    z.ai.fire_mode = "simultaneous"
    barrels = []
    for _ in range(3):
        barrel = engine.world_builder.spawn_object(world, world_coords, gun_id, False)
        barrel.ai.smoke_on_fire = True
        barrel.ai.smoke_type = "cannon"
        barrel.ai.smoke_offset = [-40, 0]
        barrel.ai.spawn_case = False
        barrels.append(barrel)
    z.ai.adopt_barrels(barrels)
    z.ai.rate_of_fire = barrels[0].ai.rate_of_fire
    z.rotation_angle = float(random.randint(0, 359))
    return z


@register_object("mg151_15_drilling")
def create_15(world, world_coords):
    # Three MG 151/15. Early Sd.Kfz. 251/21 armament.
    return _create(
        world,
        world_coords,
        "mg151_15",
        "MG 151/15 Drilling",
        "A triple MG 151/15 mount. The guns fire together.",
    )


@register_object("mg151_20_drilling")
def create_20(world, world_coords):
    # Three MG 151/20. The later Sd.Kfz. 251/21 armament.
    return _create(
        world,
        world_coords,
        "mg151_20",
        "MG 151/20 Drilling",
        "A triple MG 151/20 mount. The guns fire together.",
    )
