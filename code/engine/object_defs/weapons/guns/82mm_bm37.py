"""
82mm_bm37 object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("82mm_bm37")
def create(world, world_coords):
    # ref : https://en.wikipedia.org/wiki/82-BM-37
    # 82-BM-37 battalion mortar. O-832D bomb, max range about 3040 m.
    # indirect_range is the GrW 34 scale (2400 m -> 4500) applied to 3040 m.
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "82-BM-37"
    z.no_update = True
    z.is_gun = True
    z.ai.mechanical_accuracy = 10
    z.ai.mechanical_accuracy_deg = 0.30
    z.ai.magazine = engine.world_builder.spawn_object(world, world_coords, "82mm_bm37_magazine", False)
    z.ai.rate_of_fire = 1
    z.ai.range = 4000
    z.ai.indirect_range = 5700
    # historical min ~85 m; same game-scale floor as the GrW 34
    z.ai.minimum_range = 400
    z.ai.type = "cannon"
    z.ai.use_antitank = False
    z.ai.use_antipersonnel = True
    z.ai.direct_fire = False
    z.ai.indirect_fire = True
    z.ai.indirect_fire_mode = True
    z.rotation_angle = 0
    return z
