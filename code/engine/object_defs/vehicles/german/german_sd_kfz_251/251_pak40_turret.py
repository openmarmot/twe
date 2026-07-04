"""
251_pak40_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("251_pak40_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
    z = WorldObject(
        world, ["pak40_vehicle_turret", "pak40_vehicle_turret"], AITurret
    )
    z.name = "PAK 40 turret"
    z.is_turret = True
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_zf_38", False)
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 1
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [13, 0, 0]
    z.ai.turret_armor["left"] = [6, 22, 0]
    z.ai.turret_armor["right"] = [6, 22, 0]
    z.ai.turret_armor["front"] = [6, 36, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    z.ai.position_offset = [0, 0]
    z.ai.rotation_range = [-30, 30]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "75mm_pak40", False)
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-70, 0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon_reload_speed = 20
    z.ai.primary_turret = True
    z.no_save = True
    return z
