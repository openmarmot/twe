"""
75mm_leig18 object definition

repo : https://github.com/openmarmot/twe

notes :
7.5 cm le.IG 18. short infantry howitzer, L/11.8, muzzle velocity
about 221 m/s. Practical rate 8-12 rpm. Direct fire is for the
fight in front of the gun. Indirect fire reaches the charge-5
maximum of 3550 m, on the same scale as the ZiS-3's 13000.
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_gun import AIGun
import engine.world_builder
from engine.object_registry import register_object


@register_object("75mm_leig18")
def create(world, world_coords):
    z = WorldObject(world, ["mg34"], AIGun)
    z.name = "7.5 cm leIG 18"
    z.no_update = True
    z.is_gun = True
    # shorter and slower than the KwK 37 L/24 (mechanical_accuracy 10, 0.30 deg)
    z.ai.mechanical_accuracy = 10
    z.ai.mechanical_accuracy_deg = 0.45
    z.ai.magazine = engine.world_builder.spawn_object(
        world, world_coords, "75mm_leig18_magazine", False
    )
    z.ai.rate_of_fire = 1
    z.ai.reload_speed = 8
    z.ai.range = 4000
    z.ai.indirect_range = 5000
    z.ai.minimum_range = 400
    z.ai.type = "cannon"
    # infantry gun. soft targets first. HEAT is still in the rack.
    z.ai.use_antitank = False
    z.ai.use_antipersonnel = True
    z.ai.direct_fire = True
    z.ai.indirect_fire = True
    z.ai.indirect_fire_mode = False
    z.rotation_angle = 0
    return z
