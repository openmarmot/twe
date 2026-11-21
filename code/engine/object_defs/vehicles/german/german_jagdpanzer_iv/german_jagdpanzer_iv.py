"""
german_jagdpanzer_iv object definition

repo : https://github.com/openmarmot/twe

Sd.Kfz. 162 with the 7.5 cm Pak 39 L/48. Not the Panzer IV/70.
"""

# import built in modules
import random

# import custom packages
from engine.world_object import WorldObject
from ai.ai_vehicle import AIVehicle
from engine.vehicle_role import VehicleRole
import engine.world_builder
from engine.object_registry import register_object


@register_object("german_jagdpanzer_iv")
def create(world, world_coords):
    # ref : https://tanks-encyclopedia.com/ww2/nazi_germany/jagdpanzer-iv.php
    # January-April 1944. May 1944 (chassis 320301) is german_jagdpanzer_iv_late.
    z = WorldObject(world, ["jagdpanzer_iv_chassis"], AIVehicle)
    z.name = "Jagdpanzer IV"
    z.is_vehicle = True
    z.is_towable = True
    z.ai.requires_afv_training = True
    z.ai.passenger_compartment_ammo_racks = True
    # [armor in mm, angle in degrees with 0 being vertical, spaced armor in mm]
    # vehicle_armor is the lower half. passenger_compartment_armor is the casemate.
    # lower nose 50 mm at 55 is about 87 mm line of sight.
    z.ai.vehicle_armor["top"] = [10, 0, 0]
    z.ai.vehicle_armor["bottom"] = [10, 0, 0]
    z.ai.vehicle_armor["left"] = [30, 0, 5]
    z.ai.vehicle_armor["right"] = [30, 0, 5]
    z.ai.vehicle_armor["front"] = [50, 55, 0]
    z.ai.vehicle_armor["rear"] = [20, 11, 0]
    # casemate front 60 mm at 50 is about 93 mm line of sight.
    # early casemate sides are 30 mm at 30. the May 1944 batch went to 40 mm.
    # casemate rear 30 mm at 10. roof 20 mm.
    z.ai.passenger_compartment_armor["top"] = [20, 0, 0]
    z.ai.passenger_compartment_armor["bottom"] = [20, 0, 0]
    z.ai.passenger_compartment_armor["left"] = [30, 30, 0]
    z.ai.passenger_compartment_armor["right"] = [30, 30, 0]
    z.ai.passenger_compartment_armor["front"] = [60, 50, 0]
    z.ai.passenger_compartment_armor["rear"] = [30, 10, 0]
    main_turret = engine.world_builder.spawn_object(world, world_coords, "jagdpanzer_iv_main_gun", True)
    z.ai.turrets.append(main_turret)
    main_turret.ai.vehicle = z
    # roof Rundumsfeuer MG 42. the sprite is the remote MG 34 mount.
    mg_turret = engine.world_builder.spawn_object(world, world_coords, "remote_mg42_turret", True)
    z.ai.turrets.append(mg_turret)
    mg_turret.ai.vehicle = z
    mg_turret.ai.position_offset = [6, 17]
    z.ai.radio = engine.world_builder.spawn_object(world, world_coords, "radio_feldfu_b", False)

    role = VehicleRole("driver", z)
    role.is_driver = True
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("gunner", z)
    role.is_gunner = True
    role.turret = main_turret
    z.ai.vehicle_crew.append(role)

    # the loader fired the roof gun from inside. one seat does one job,
    # so this seat stays on the MG. the commander can take the Pak if the gunner is lost.
    role = VehicleRole("loader", z)
    role.is_gunner = True
    role.turret = mg_turret
    z.ai.vehicle_crew.append(role)

    role = VehicleRole("commander", z)
    role.is_commander = True
    role.is_radio_operator = True
    role.radio = z.ai.radio
    z.ai.vehicle_crew.append(role)

    # same HL 120 and chassis family as the Panzer IV. shared road and off-road figures.
    z.ai.max_speed = 367.04
    z.ai.max_offroad_speed = 177.6
    # z.ai.rotation_speed=30. # !! note rotation speeds <40 seem to cause ai to lose control
    z.ai.rotation_speed = 40.0
    z.collision_radius = 100
    # hull about 6 m long and 3.2 m wide. radius 42 is the width.
    z.bounding_circles.append([[-50.0, 0.0], 42])
    z.bounding_circles.append([[-18.0, 0.0], 42])
    z.bounding_circles.append([[14.0, 0.0], 42])
    z.bounding_circles.append([[46.0, 0.0], 42])
    z.weight = 24000
    z.drag_coefficient = 0.9
    z.frontal_area = 5
    z.ai.fuel_tanks.append(
        engine.world_builder.spawn_object(world, world_coords, "vehicle_fuel_tank", False)
    )
    z.ai.fuel_tanks[0].volume = 114
    engine.world_builder.fill_container(world, z.ai.fuel_tanks[0], "gas_80_octane")
    z.ai.engines.append(
        engine.world_builder.spawn_object(world, world_coords, "maybach_hl120_trm_engine", False)
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
    for b in range(10):
        z.add_inventory(engine.world_builder.spawn_object(world, world_coords, "mg34_belt", False))
    # 79 rounds. panzerjäger mix: Pzgr. 39, a few Pzgr. 40, the rest Sprgr. 34.
    z.ai.ammo_rack_capacity = 79
    for b in range(40):
        z.ai.ammo_rack.append(
            engine.world_builder.spawn_object(world, world_coords, "7.5cm_pak39_L48_magazine", False)
        )
    for b in range(4):
        temp = engine.world_builder.spawn_object(world, world_coords, "7.5cm_pak39_L48_magazine", False)
        engine.world_builder.load_magazine(world, temp, "PzGr40_75_L48")
        z.ai.ammo_rack.append(temp)
    for b in range(35):
        temp = engine.world_builder.spawn_object(world, world_coords, "7.5cm_pak39_L48_magazine", False)
        engine.world_builder.load_magazine(world, temp, "Sprgr_34_75_L48")
        z.ai.ammo_rack.append(temp)
    z.ai.min_wheels_per_side_front = 3
    z.ai.min_wheels_per_side_rear = 3
    z.ai.max_wheels = 16
    z.ai.max_spare_wheels = 0
    for b in range(4):
        z.ai.front_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
        z.ai.front_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
        z.ai.rear_left_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
        z.ai.rear_right_wheels.append(
            engine.world_builder.spawn_object(world, world_coords, "panzeriv_wheel", False)
        )
    return z
