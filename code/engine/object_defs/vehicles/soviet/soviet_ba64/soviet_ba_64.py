"""
soviet_ba_64 object definition

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


@register_object("soviet_ba_64")
def create(world, world_coords):
    z = WorldObject(world, ["ba_64_chassis"], AIVehicle)
    z.name = "BA-64"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.open_top = True
    z.ai.cramped_crew_compartment = True
    z.ai.vehicle_armor["top"] = [4, 0, 0]
    z.ai.vehicle_armor["bottom"] = [4, 0, 0]
    z.ai.vehicle_armor["left"] = [6, 30, 0]
    z.ai.vehicle_armor["right"] = [6, 30, 0]
    z.ai.vehicle_armor["front"] = [9, 30, 0]
    z.ai.vehicle_armor["rear"] = [6, 30, 0]
    z.ai.passenger_compartment_armor["top"] = [4, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [4, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [9, 30, 0]
    z.ai.passenger_compartment_armor["right"] = [9, 30, 0]
    z.ai.passenger_compartment_armor["front"] = [12, 30, 0]
    z.ai.passenger_compartment_armor["rear"] = [9, 34, 0]
    z.ai.max_speed = 385.9
    z.ai.max_offroad_speed = 177.6
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    z.bounding_circles.append([[-43.0, 0.0], 25])
    z.bounding_circles.append([[-20.0, 0.0], 25])
    z.bounding_circles.append([[0.0, 0.0], 25])
    z.bounding_circles.append([[21.0, 0.0], 25])
    z.bounding_circles.append([[39.0, 0.0], 25])
    z.weight = 4800
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 114
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "maybach_hl42_engine", False)
    )
    z.ai.engines[0].ai.exhaust_position_offset = [75, 10]
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_6v", False)
    )
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "german_fuel_can", False))
    z.add_inventory(engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_medical, False))
    z.add_inventory(
        engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_consumables, False)
    )
    z.rotation_angle = float(random.randint(0, 359))
    if random.randint(0, 1) == 1:
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "ppsh41", False))
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 4
    z.ai.max_spare_wheels = 1
    z.ai.front_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    z.ai.front_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    z.ai.rear_left_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    z.ai.rear_right_wheels.append(
        engine.world_builder.spawn_object(world, world_coords, "251_wheel", False)
    )
    z.ai.passenger_compartment_ammo_racks = True
    z.ai.requires_afv_training = True
    z.ai.is_transport = False
    turret = engine.world_builder.spawn_object(world, world_coords, "ba_64_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z
    z.ai.turrets[0].ai.position_offset = [19, 0]

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.is_commander = True
    role.turret = turret
    role.seat_offset = [-5, -1]
    role.seat_visible = True
    role.seat_rotates_with_turret = True

    z.ai.vehicle_crew.append(role)

    # mg ammo
    for b in range(20):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "dtm_magazine", False))
    return z
