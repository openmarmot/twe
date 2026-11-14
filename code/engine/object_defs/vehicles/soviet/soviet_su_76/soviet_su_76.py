"""
soviet_su_76 object definition

repo : https://github.com/openmarmot/twe

SU-76M with a closed fighting compartment. The usual SU-76M was open.
Some late vehicles carried a thin roof, and the sprite here has one.
Sprites: su_76_chassis.png and su_76_gun.png.
The gun is the ZiS-3, same rounds and ballistics as 76mm_m1940_f34.
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("soviet_su_76")
def create(world, world_coords):
    # ref : Osprey SU-76M; hull width in notes.txt is 2714 mm
    z = WorldObject(world, ["su_76_chassis"], AIVehicle)
    z.name = "SU-76"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.requires_afv_training = True
    # closed top. most SU-76M were open. this sprite has a roof, and some
    # late vehicles did too: a 4 mm factory trial, a 6 mm early-series roof,
    # or about 10 mm of field boiler plate. grenades do not fall inside.
    z.ai.open_top = False
    z.ai.passenger_compartment_ammo_racks = True
    # angles are degrees from vertical. low hits use the hull.
    # lower nose 30 mm at 30 is about 35 mm line of sight.
    # hull sides are the T-70 plate, thinned to 15 mm. rear 15 mm at 30.
    # engine deck and floor are 7 mm.
    z.ai.vehicle_armor["top"] = [7, 0, 0]
    z.ai.vehicle_armor["bottom"] = [7, 0, 0]
    z.ai.vehicle_armor["left"] = [15, 0, 0]
    z.ai.vehicle_armor["right"] = [15, 0, 0]
    z.ai.vehicle_armor["front"] = [30, 30, 0]
    z.ai.vehicle_armor["rear"] = [15, 30, 0]
    # high hits. upper glacis 25 mm at 60 is about 50 mm line of sight.
    # the casemate face behind it is 25 mm at 25 and is not its own zone.
    # casemate sides 10 mm at 20. casemate rear 15 mm.
    # casemate roof is 6 mm, the early roofed fighting compartment.
    z.ai.passenger_compartment_armor["top"] = [6, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [7, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [10, 20, 0]
    z.ai.passenger_compartment_armor["right"] = [10, 20, 0]
    z.ai.passenger_compartment_armor["front"] = [25, 60, 0]
    z.ai.passenger_compartment_armor["rear"] = [15, 0, 0]
    main_turret = engine.world_builder.spawn_object(world, world_coords, "su_76_turret", True)
    z.ai.turrets.append(main_turret)
    main_turret.ai.vehicle = z

    # crew of four. no hull machine gun. the driver sits front left.
    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = main_turret
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("assistant_gunner", z)
    role.is_assistant_gunner = True
    z.ai.vehicle_crew.append(role)

    # 45 km/h on the road. 1 mph = 11.84 game units/s.
    # cross-country average is about 21 km/h. the T-70 cap is 177.6.
    z.ai.max_speed = 331.0
    z.ai.max_offroad_speed = 160.0
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    # hull sprite is about 144 px long and 74 px wide, centered.
    # radius 37 is the half-width. local -x is the front.
    z.bounding_circles.append([[-36.0, 0.0], 37])
    z.bounding_circles.append([[-12.0, 0.0], 37])
    z.bounding_circles.append([[12.0, 0.0], 37])
    z.bounding_circles.append([[36.0, 0.0], 37])
    # 10.6 tonnes open. a thin roof added about 200 kg.
    z.weight = 10800
    z.drag_coefficient = 0.9
    z.frontal_area = 4
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    # real tanks were about 412 liters. the game tank uses the shared 114.
    z.ai.fuel_tanks[0].volume = 114
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    # GAZ-203: two GAZ-202 gasoline sixes, 70 hp each, mounted on the right.
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "gaz_202_engine", False)
    )
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "gaz_202_engine", False)
    )
    z.ai.engines[0].ai.exhaust_position_offset = [-15, 28]
    z.ai.engines[1].ai.exhaust_position_offset = [5, 28]
    z.ai.batteries.append(
        engine.world_builder.spawn_object(world, world_coords, "battery_vehicle_6v", False)
    )
    z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "german_fuel_can", False))
    z.add_inventory(engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_medical, False))
    z.add_inventory(
        engine.world_builder.get_random_from_list(world, world_coords, engine.world_builder.list_consumables, False)
    )
    z.rotation_angle = float(random.randint(0, 359))
    # 60 rounds. infantry-support mix: mostly OF-350M, then BR-350B, a few solid.
    z.ai.ammo_rack_capacity = 60
    for b in range(36):
        temp = engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34_magazine", False)
        engine.world_builder.load_magazine(world, temp, "OF-350M")
        z.ai.ammo_rack.append(temp)
    for b in range(20):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34_magazine", False)
        )
    for b in range(4):
        temp = engine.world_builder.spawn_object(world, world_coords, "76mm_m1940_f34_magazine", False)
        engine.world_builder.load_magazine(world, temp, "76x385_AP")
        z.ai.ammo_rack.append(temp)
    # six road wheels a side, same wheel object the T-70 uses
    z.ai.min_wheels_per_side_front = 2
    z.ai.min_wheels_per_side_rear = 2
    z.ai.max_wheels = 12
    z.ai.max_spare_wheels = 0
    for b in range(3):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t34_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t34_wheel", False)
        )
        z.ai.rear_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t34_wheel", False)
        )
        z.ai.rear_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "t34_wheel", False)
        )
    return z
