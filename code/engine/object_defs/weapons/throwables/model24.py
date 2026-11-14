"""
model24 object definition

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


@register_object("model24")
def create(world, world_coords):
    z = WorldObject(world, ["model24"], AIThrowable)
    z.name = "model24"
    z.description = "A German Model 24 stick grenade. Blast charge, thin case, no fragmentation sleeve."
    z.minimum_visible_scale = 0.4
    z.is_grenade = True
    z.is_throwable = True
    z.ai.explosive = True
    # 165 g TNT in a 0.8 mm can. This is a blast grenade.
    # About 15 psi (lethal) at 1.1 m, about 2 psi (casualty) at 3.3 m.
    # The Splitterring, which is not modeled, is what pushed fragments out to about 35 m.
    z.ai.lethal_radius = 1.1 * METER
    z.ai.explosion_radius = 3.3 * METER
    z.ai.edge_power = 40
    # thin case, a few secondary splinters. Dockery gives 10-15 m.
    z.ai.shrapnel_count = 8
    z.ai.fragment_range = 12 * METER
    # B.Z. 24 delay is 4-5 seconds. A full throw is about 30 m in 2 seconds.
    z.ai.fuse_max_time = 4.5
    z.ai.max_flight_time = 2.0
    z.ai.range = 30 * METER
    z.ai.max_speed = z.ai.range / z.ai.max_flight_time
    # outside the blast, and usually clear of his own splinters if he gets down
    z.ai.min_range = 8 * METER
    z.ai.has_fuse = True
    z.ai.use_antipersonnel = True
    z.rotation_angle = float(random.randint(0, 359))
    return z
