"""
nahverteidigungswaffe_turret object definition

repo : https://github.com/openmarmot/twe
"""

# import custom packages
from engine.world_object import WorldObject
from ai.ai_turret import AITurret
import engine.world_builder
from engine.object_registry import register_object


@register_object("nahverteidigungswaffe_turret")
def create(world, world_coords):
    # !! note - turrets should be spawned with spawn TRUE as they are always in world
    # this is the late war german smoke/he mortar device
    z = WorldObject(world, ["panzer_iv_hull_mg"], AITurret)
    z.name = "Nahverteidigungswaffe Turret"
    z.ai.gun_sight = engine.world_builder.spawn_object(world, world_coords, "optic_iron_sights", False)
    z.render = False  # this turret is small enough to be basically invisible from outside a tank. its just a circle with a hole in it.
    z.is_turret = True
    z.ai.small = True
    z.ai.vehicle_mount_side = "center"  # this makes it un-hittable
    z.ai.turret_accuracy = 30
    z.ai.turret_armor["top"] = [16, 0, 0]
    z.ai.turret_armor["bottom"] = [8, 0, 0]
    z.ai.turret_armor["left"] = [5, 0, 0]
    z.ai.turret_armor["right"] = [5, 0, 0]
    z.ai.turret_armor["front"] = [5, 0, 0]
    z.ai.turret_armor["rear"] = [5, 0, 0]
    z.ai.position_offset = [0, 0]
    z.ai.rotation_range = [-360, 360]
    z.ai.primary_weapon = engine.world_builder.spawn_object(
        world, world_coords, "nahverteidigungswaffe", False
    )
    z.ai.primary_weapon.ai.equipper = z
    z.ai.primary_weapon.ai.spawn_case = False
    z.ai.primary_weapon_reload_speed = 5
    z.no_save = True
    return z
