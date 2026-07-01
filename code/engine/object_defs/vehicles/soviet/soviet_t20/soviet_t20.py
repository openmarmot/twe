"""
soviet_t20 object definition

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


@register_object("soviet_t20")
def create(world, world_coords):
    # ref : https://en.wikipedia.org/wiki/Komsomolets_armored_tractor
    # ref : https://wiki.warthunder.com/ZiS-30
    z = WorldObject(world, ["t20", "t20_destroyed"], AIVehicle)
    z.name = "T20 Komsomolets armored tractor"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.is_transport = True
    z.ai.open_top = True
    z.ai.vehicle_armor["top"] = [5, 0, 0]
    z.ai.vehicle_armor["bottom"] = [7, 0, 0]
    z.ai.vehicle_armor["left"] = [7, 19, 0]
    z.ai.vehicle_armor["right"] = [7, 19, 0]
    z.ai.vehicle_armor["front"] = [10, 24, 0]
    z.ai.vehicle_armor["rear"] = [7, 42, 0]
    z.ai.passenger_compartment_armor["top"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [5, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["right"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["front"] = [0, 0, 0]
    z.ai.passenger_compartment_armor["rear"] = [0, 0, 0]
    turret = engine.world_builder.spawn_object(world, world_coords, "t20_turret", True)
    z.ai.turrets.append(turret)
    turret.ai.vehicle = z

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = turret
    z.ai.vehicle_crew.append(role)

    passenger_positions = [
        [0, -17],
        [11, -17],
        [24, -17],
        [0, 17],
        [11, 17],
        [24, 17],
    ]
    passenger_rotation = [90, 90, 90, 270, 270, 270]
    for x in range(6):
        role = VehicleRole("passenger", z)
        role.is_passenger = True
        role.seat_visible = True
        role.seat_rotation = passenger_rotation.pop()
        role.seat_offset = passenger_positions.pop()
        z.ai.vehicle_crew.append(role)

    z.ai.max_speed = 367.04
    z.ai.max_offroad_speed = 177.6
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    z.bounding_circles.append([[-22.0, 0.0], 25])
    z.bounding_circles.append([[0.0, 0.0], 25])
    z.bounding_circles.append([[25.0, 0.0], 25])
    z.weight = 3500
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

    # turret ammo
    for b in range(4):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "dtm_magazine", False))
    z.ai.min_wheels_per_side_front = 1
    z.ai.min_wheels_per_side_rear = 1
    z.ai.max_wheels = 8
    z.ai.max_spare_wheels = 0
    for b in range(2):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t20_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t20_wheel", False)
        )
        z.ai.rear_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t20_wheel", False)
        )
        z.ai.rear_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t20_wheel", False)
        )
    return z
