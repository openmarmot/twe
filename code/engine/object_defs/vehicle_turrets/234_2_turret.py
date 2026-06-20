"""
234_2_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("234_2_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["sd_kfz_234_2_turret", "sd_kfz_234_2_turret"], AITurret)
    z.name = "Sd.Kfz.234/2 Turret"
    z.is_turret = True
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_tzf_6", False)
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 1
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [0, 0, 0]
    z.ai.turret_armor["left"] = [8, 19, 0]
    z.ai.turret_armor["right"] = [8, 19, 0]
    z.ai.turret_armor["front"] = [30, 55, 0]
    z.ai.turret_armor["rear"] = [10, 46, 0]
    z.ai.position_offset = [0, 0]
    z.ai.rotation_range = [-360, 360]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "5cm_kwk39_l60", False)
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-0, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon_reload_speed = 5
    z.ai.primary_turret = True
    z.no_save = True
    return z
