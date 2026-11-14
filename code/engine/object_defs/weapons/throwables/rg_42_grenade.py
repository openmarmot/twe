"""
rg_42_grenade object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_throwable import AIThrowable
from engine.object_registry import register_object


# 1 foot = 8.0608 game units, so 1 meter is 26.45 units.
METER = 26.45


@register_object("rg_42_grenade")
def create(world, world_coords):
    z = WorldObject(world, ["rg_42_grenade"], AIThrowable)
    z.name = "RG-42 Grenade"
    z.description = "A Soviet RG-42 fragmentation grenade with a scored liner."
    z.minimum_visible_scale = 0.4
    z.is_grenade = True
    z.is_throwable = True
    z.ai.explosive = True
    # about 118 g TNT. Lethal blast near 1 m, casualty blast near 3 m.
    # smaller charge than the stick grenade, so the blast is the smaller part.
    z.ai.lethal_radius = 1.0 * METER
    z.ai.explosion_radius = 3.0 * METER
    z.ai.edge_power = 40
    # three-layer scored liner. Brassey's gives a 20 m fragmentation range.
    # 25 m is the outer danger, not a ring of certain hits. 24 pieces stand in
    # for the liner: enough that a man in the open inside 10 m is likely hit.
    z.ai.shrapnel_count = 24
    z.ai.fragment_range = 20 * METER
    # UZRG delay is 3.2-4.2 seconds. A normal throw is about 25 m in 2 seconds.
    # Manuals put a hard throw at 30-40 m.
    z.ai.fuse_max_time = 3.7
    z.ai.max_flight_time = 2.0
    z.ai.range = 25 * METER
    z.ai.max_speed = z.ai.range / z.ai.max_flight_time
    # a defensive grenade. inside this the thrower is in his own fragment pattern.
    z.ai.min_range = 15 * METER
    z.ai.has_fuse = True
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
