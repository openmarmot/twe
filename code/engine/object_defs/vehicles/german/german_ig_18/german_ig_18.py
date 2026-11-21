"""
german_ig_18 object definition

repo : https://github.com/openmarmot/twe

notes :
7.5 cm le.IG 18 in firing order. 400 kg. The wheels are drawn on
the chassis sprite, so this piece has no separate wheel objects.
Crew push it. The trail, axle, and spade stay with the chassis.
The shield, barrel, and cradle are the turret.
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_ig_18")
def create(world, world_coords):
    z = WorldObject(world, ["ig18_chassis"], AIVehicle)
    z.name = "7.5 cm leIG 18"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.is_towed_gun = True
    z.ai.requires_afv_training = False
    # low hits land here. the lower front apron is the same shield
    # face as the turret, 4 mm at 15 degrees. the trail and wheels
    # are open, so the sides stay at zero.
    z.ai.vehicle_armor["top"] = [0, 0, 0]
    z.ai.vehicle_armor["bottom"] = [0, 0, 0]
    z.ai.vehicle_armor["left"] = [0, 0, 0]
    z.ai.vehicle_armor["right"] = [0, 0, 0]
    z.ai.vehicle_armor["front"] = [4, 15, 0]
    z.ai.vehicle_armor["rear"] = [0, 0, 0]
    turret = engine.world_builder.spawn_object(
        world, world_coords, "ig18_turret", True
    )
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    # seats are a first placement. nudge them in image_tool.
    role = VehicleRole("driver", z)
    role.is_driver = True
    role.seat_visible = True
    role.seat_offset = [11, 13]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [-8, -10]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    role.seat_visible = True
    role.seat_offset = [-8, 10]
    z.ai.vehicle_crew.append(role)

    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "bicycle_pedals", False)
    )
    # crew push, 400 kg. the 1120 kg ZiS-3 is 85. this is a step quicker.
    z.ai.max_speed = 95
    z.ai.max_offroad_speed = 95
    z.ai.open_top = True
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 40
    z.bounding_circles.append([[-18, 0.0], 25])
    z.weight = 400
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.rotation_angle = float(random.randint(0, 359))
    # 20 HE and 4 HEAT beside the breech round. a limber would carry more.
    z.ai.ammo_rack_capacity = 24
    for _ in range(20):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(
                world, world_coords, "75mm_leig18_magazine", False
            )
        )
    for _ in range(4):
        temp = engine.world_builder.spawn_object(
            world, world_coords, "75mm_leig18_magazine", False
        )
        engine.world_builder.load_magazine(world, temp, "Igr_38_HlA")
        z.ai.ammo_rack.append(temp)
    # wheels are painted on ig18_chassis.png
    z.ai.max_wheels = 0
    z.ai.max_spare_wheels = 0
    return z
