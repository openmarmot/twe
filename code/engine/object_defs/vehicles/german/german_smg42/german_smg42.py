"""
german_smg42 object definition

repo : https://github.com/openmarmot/twe
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_smg42")
def create(world, world_coords):
    # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/sdkfz-251_hanomag.php
    z = WorldObject(world, ["smg42_base"], AIVehicle)
    z.name = "Schweres MG42 on Lafette mount"
    z.is_vehicle = True
    z.is_towable = False
    turret = engine.world_builder.spawn_object(world, world_coords, "smg42_turret", True)
    turret.ai.position_offset = [0, 0]
    turret.ai.rotation_range = [-30, 30]
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    role.seat_visible = True
    role.seat_offset = [28.8, 20.0]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    role.seat_visible = True
    role.seat_offset = [19.6, -0.4]
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    role.seat_visible = True
    role.seat_offset = [27.6, -28.0]
    z.ai.vehicle_crew.append(role)

    z.ai.engines.append(engine.world_builder.spawn_object(world, world_coords, "bicycle_pedals", False))
    z.ai.max_speed = 100
    z.ai.max_offroad_speed = 100
    z.ai.open_top = True
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 50
    z.bounding_circles.append([[0.0, 0.0], 25])
    z.weight = 1400
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.rotation_angle = float(random.randint(0, 359))
    z.ai.ammo_rack_capacity = 30
    # mg ammo
    for b in range(10):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))
    # armor piercing belt
    if random.randint(0, 1) == 1:
        belt = engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False)
        engine.world_builder.load_magazine(world, belt, "7.92x57_SMK")
        z.add_inventory(belt)
    z.ai.max_wheels = 0
    z.ai.max_spare_wheels = 0
    return z
