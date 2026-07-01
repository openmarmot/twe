"""
remote_mg34_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("remote_mg34_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    z = WorldObject(world, ["remote_mg34_turret", "remote_mg34_turret"], AITurret)
    z.name = "Remote MG34 Turret"
    z.is_turret = True
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_iron_sights", False)
    z.ai.vehicle_mount_side = "top"
    z.ai.turret_accuracy = 12
    z.ai.remote_operated = True
    z.ai.small = True
    z.ai.turret_armor["top"] = [0, 0, 0]
    z.ai.turret_armor["bottom"] = [0, 0, 0]
    z.ai.turret_armor["left"] = [15, 60, 0]
    z.ai.turret_armor["right"] = [15, 60, 0]
    z.ai.turret_armor["front"] = [15, 60, 0]
    z.ai.turret_armor["rear"] = [0, 0, 0]
    # this weapon is shared, so set this when you add the turret
    # z.ai.position_offset=[-65,13] # Best to set this when you spawn per vehicle
    z.ai.rotation_range = [-360, 360]
    z.ai.primary_weapon = engine.world_builder.spawn_object(world, world_coords, "mg34", False)
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon_reload_speed = 10
    z.no_save = True
    return z
