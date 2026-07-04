"""
t20_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("t20_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["t20_turret", "t20_turret"], AITurret)
    z.name = "T20 Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_iron_sights", False)
    z.is_turret = True
    z.ai.small = True
    z.ai.vehicle_mount_side = "front"
    z.ai.turret_accuracy = 10
    z.ai.turret_armor["top"] = [5, 31, 0]
    z.ai.turret_armor["bottom"] = [5, 31, 0]
    z.ai.turret_armor["left"] = [5, 31, 0]
    z.ai.turret_armor["right"] = [5, 31, 0]
    z.ai.turret_armor["front"] = [5, 31, 0]
    z.ai.turret_armor["rear"] = [5, 31, 0]
    z.ai.position_offset = [-25, 9]
    z.ai.rotation_range = [-20, 20]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "dtm", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_turret = True
    z.ai.primary_weapon_reload_speed = 10
    z.no_save = True
    return z
