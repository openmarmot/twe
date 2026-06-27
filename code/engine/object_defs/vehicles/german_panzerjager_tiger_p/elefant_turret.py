"""
elefant_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("elefant_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["elefant_turret"], AITurret)
    z.name = "Elefant Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_sfl_zf_1a", False)
    z.is_turret = True
    z.ai.vehicle_mount_side = "front"
    z.ai.turret_accuracy = 1
    z.ai.turret_armor["top"] = [20, 0, 0]
    z.ai.turret_armor["bottom"] = [20, 0, 0]
    z.ai.turret_armor["left"] = [200, 0, 0]
    z.ai.turret_armor["right"] = [200, 0, 0]
    z.ai.turret_armor["front"] = [200, 0, 10]  # has a odd spaced front plate
    z.ai.turret_armor["rear"] = [200, 0, 0]
    z.ai.position_offset = [0, 0]
    z.ai.rotation_range = [-14, 14]
    z.ai.primary_weapon = engine.world_builder.spawn_object(
        world, world_coords, "8.8cm_pak43_l71", False
    )
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.smoke_on_fire = True
    z.ai.primary_weapon.ai.smoke_type = "cannon"
    z.ai.primary_weapon.ai.smoke_offset = [-100.0, 1.0]
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 20
    z.ai.coaxial_weapon_reload_speed = 10
    z.no_save = True
    return z
