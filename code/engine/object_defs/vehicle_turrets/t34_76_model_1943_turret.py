"""
t34_76_model_1943_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("t34_76_model_1943_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(
        world, ["t34_76_model_1943_turret", "t34_76_model_1943_turret"], AITurret
    )
    z.name = "T34-76 Model 1943 turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_tmfd_7", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 2
    z.ai.turret_armor["top"] = [15, 0, 0]
    z.ai.turret_armor["bottom"] = [8, 0, 0]
    z.ai.turret_armor["left"] = [53, 21, 0]
    z.ai.turret_armor["right"] = [53, 21, 0]
    z.ai.turret_armor["front"] = [53, 20, 0]
    z.ai.turret_armor["rear"] = [53, 20, 0]
    z.ai.position_offset = [-15, 0]
    z.ai.rotation_range = [-360, 360]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-82, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.coaxial_weapon = engine.world_builder.spawn_object(world, world_coords, "dtm", False)
    z.ai.coaxial_weapon.ai.spawn_case = False
    z.ai.coaxial_weapon.ai.equipper = z
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 25
    z.ai.coaxial_weapon_reload_speed = 10
    z.no_save = True
    return z
