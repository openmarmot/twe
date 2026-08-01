"""
234_1_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("234_1_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["sd_kfz_234_1_turret", "sd_kfz_234_1_turret"], AITurret)
    z.name = "Sd.Kfz.234/1 Turret"
    z.is_turret = True
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_tzf_6", False)
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 2
    z.ai.turret_armor["top"] = [1, 0, 0]
    z.ai.turret_armor["bottom"] = [13, 0, 0]
    z.ai.turret_armor["left"] = [8, 33, 0]
    z.ai.turret_armor["right"] = [8, 33, 0]
    z.ai.turret_armor["front"] = [30, 33, 0]
    z.ai.turret_armor["rear"] = [8, 33, 0]
    z.ai.position_offset = [-16, 0]
    z.ai.rotation_range = [-360, 360]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "2cm_kwk38_l55", False)
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-70, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon_reload_speed = 10
    z.ai.primary_turret = True
    z.ai.coaxial_weapon = engine.world_builder.spawn_object(world, world_coords, "mg34", False)
    z.ai.coaxial_weapon.ai.equipper = z
    z.ai.coaxial_weapon.ai.spawn_case = False
    z.ai.coaxial_weapon_reload_speed = 10
    z.no_save = True
    return z
