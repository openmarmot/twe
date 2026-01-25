
'''
repo : https://github.com/openmarmot/twe

notes :
all the code for self debug of the world state. this can be triggered through the debug menu (~)
'''

import engine.math_2d

#---------------------------------------------------------------------------
def run_object_counts_report(world):
    '''generates a list of objects in world with a count per type'''

    wo_list={}
    for b in world.grid_manager.get_all_objects():
        if b.world_builder_identity in wo_list:
            wo_list[b.world_builder_identity]+=1
        else:
            wo_list[b.world_builder_identity]=1

    total_objects = sum(wo_list.values())
    print('------------------------------------')
    print(f'world object count. total : {total_objects}')
    print('------------------------------------')

    for key,value in sorted(wo_list.items(), key=lambda item: item[1], reverse=True):
        print(key,'count:',value)
    print('------------------------------------')

#---------------------------------------------------------------------------
def check_task_vehicle_crew(b, issues, world):
    '''sanity checks for task_vehicle_crew'''
    if 'vehicle_role' not in b.ai.memory['task_vehicle_crew']:
        issues.append(f'{b.name} missing vehicle_role in task_vehicle_crew memory')
    else:
        vehicle_role = b.ai.memory['task_vehicle_crew']['vehicle_role']
        if vehicle_role is None:
            issues.append(f'{b.name} vehicle_role is None')
        else:
            if vehicle_role.vehicle is None:
                issues.append(f'{b.name} vehicle_role.vehicle is None')
            else:
                if vehicle_role.vehicle not in world.grid_manager.get_all_objects():
                    issues.append(f'{b.name} vehicle not in world objects')
                if vehicle_role.vehicle.in_world is False:
                    issues.append(f'{b.name} vehicle not in world')
                if vehicle_role.role_occupied is False:
                    issues.append(f'{b.name} vehicle_role not occupied')
                if vehicle_role.human != b:
                    issues.append(f'{b.name} vehicle_role.human mismatch')
                if vehicle_role not in vehicle_role.vehicle.ai.vehicle_crew:
                    issues.append(f'{b.name} vehicle_role not in vehicle crew')
                # check distance
                distance = engine.math_2d.get_distance(b.world_coords, vehicle_role.vehicle.world_coords)
                if distance > 50:  # arbitrary threshold for being "in" the vehicle
                    issues.append(f'{b.name} too far from vehicle {vehicle_role.vehicle.name} ({distance:.1f} units)')

#---------------------------------------------------------------------------
def check_task_enter_vehicle(b, issues, world):
    '''sanity checks for task_enter_vehicle'''
    if 'vehicle' not in b.ai.memory['task_enter_vehicle']:
        issues.append(f'{b.name} missing vehicle in task_enter_vehicle memory')
    else:
        vehicle = b.ai.memory['task_enter_vehicle']['vehicle']
        if vehicle is None:
            issues.append(f'{b.name} vehicle is None in task_enter_vehicle')
        else:
            if vehicle not in world.grid_manager.get_all_objects():
                issues.append(f'{b.name} target vehicle not in world objects')
            if vehicle.in_world is False:
                issues.append(f'{b.name} target vehicle not in world')
            if vehicle.ai.vehicle_disabled:
                issues.append(f'{b.name} target vehicle is disabled')
            distance = engine.math_2d.get_distance(b.world_coords, vehicle.world_coords)
            if distance > b.ai.max_walk_distance:
                issues.append(f'{b.name} target vehicle too far ({distance:.1f} > {b.ai.max_walk_distance})')

#---------------------------------------------------------------------------
def check_task_move_to_location(b, issues, world):
    '''sanity checks for task_move_to_location'''
    if 'destination' not in b.ai.memory['task_move_to_location']:
        issues.append(f'{b.name} missing destination in task_move_to_location memory')
    else:
        dest = b.ai.memory['task_move_to_location']['destination']
        # check if destination is within reasonable bounds (assuming world is around 0,0 to 10000,10000 or something)
        if abs(dest[0]) > 50000 or abs(dest[1]) > 50000:
            issues.append(f'{b.name} destination out of bounds: {dest}')
        if 'moving_object' in b.ai.memory['task_move_to_location']:
            mo = b.ai.memory['task_move_to_location']['moving_object']
            if mo is not None:
                if mo not in world.grid_manager.get_all_objects():
                    issues.append(f'{b.name} moving_object not in world objects')
                if mo.in_world is False:
                    issues.append(f'{b.name} moving_object not in world')

#---------------------------------------------------------------------------
def check_task_engage_enemy(b, issues, world):
    '''sanity checks for task_engage_enemy'''
    if 'enemy' not in b.ai.memory['task_engage_enemy']:
        issues.append(f'{b.name} missing enemy in task_engage_enemy memory')
    else:
        enemy = b.ai.memory['task_engage_enemy']['enemy']
        if enemy is None:
            issues.append(f'{b.name} enemy is None in task_engage_enemy')
        else:
            if enemy not in world.grid_manager.get_all_objects():
                issues.append(f'{b.name} enemy not in world objects')
            if enemy.in_world is False:
                issues.append(f'{b.name} enemy not in world')
            if not (enemy.is_human or enemy.is_vehicle):
                issues.append(f'{b.name} enemy is neither human nor vehicle')
            distance = engine.math_2d.get_distance(b.world_coords, enemy.world_coords)
            if distance > 5000:  # arbitrary max engagement range
                issues.append(f'{b.name} enemy too far ({distance:.1f} units)')

#---------------------------------------------------------------------------
def check_vehicle_sanity(b, issues, world):
    '''sanity checks for vehicles'''
    # check crew
    for role in b.ai.vehicle_crew:
        if role.role_occupied:
            if role.human is None:
                issues.append(f'{b.name} role {role.role_name} occupied but human is None')
            else:
                if role.human not in world.grid_manager.get_all_objects():
                    issues.append(f'{b.name} crew {role.human.name} not in world objects')
                if role.human.in_world is False:
                    issues.append(f'{b.name} crew {role.human.name} not in world')
                if role.human.ai.memory.get('current_task') != 'task_vehicle_crew':
                    issues.append(f"{b.name} crew {role.human.name} memory[current_task] is {role.human.ai.memory['current_task']} not task_vehicle_crew")
                # check if human's vehicle_role points back
                if 'vehicle_role' not in role.human.ai.memory['task_vehicle_crew']:
                    issues.append(f'{b.name} crew {role.human.name} missing vehicle_role in memory')
                else:
                    if role.human.ai.memory['task_vehicle_crew']['vehicle_role'] != role:
                        issues.append(f'{b.name} crew {role.human.name} vehicle_role mismatch')

    # check engines
    for engine in b.ai.engines:
        if engine.ai.engine_on and b.ai.vehicle_disabled is False:
            if engine.ai.internal_combustion:
                if len(b.ai.fuel_tanks) == 0:
                    issues.append(f'{b.name} engine on but no fuel tanks')
                else:
                    current_fuel, max_fuel = b.ai.read_fuel_gauge()
                    if current_fuel == 0:
                        issues.append(f'{b.name} engine on but no fuel')

    # check ammo rack
    if len(b.ai.ammo_rack) > b.ai.ammo_rack_capacity:
        issues.append(f'{b.name} ammo rack over capacity: {len(b.ai.ammo_rack)} > {b.ai.ammo_rack_capacity}')

    # check towed object
    if b.ai.towed_object is not None:
        if b.ai.towed_object not in world.grid_manager.get_all_objects():
            issues.append(f'{b.name} towed_object not in world objects')
        if b.ai.towed_object.in_world is False:
            issues.append(f'{b.name} towed_object not in world')
        distance = engine.math_2d.get_distance(b.world_coords, b.ai.towed_object.world_coords)
        if distance > 200:  # arbitrary tow distance
            issues.append(f'{b.name} towed_object too far ({distance:.1f} units)')

    # check wheels if present
    total_wheels = (len(b.ai.front_left_wheels) + len(b.ai.front_right_wheels) +
                    len(b.ai.rear_left_wheels) + len(b.ai.rear_right_wheels))
    if total_wheels > 0:
        healthy_wheels = 0
        for wheel in (b.ai.front_left_wheels + b.ai.front_right_wheels +
                      b.ai.rear_left_wheels + b.ai.rear_right_wheels):
            if not wheel.ai.destroyed:
                healthy_wheels += 1
        if healthy_wheels < b.ai.min_wheels_per_side_front + b.ai.min_wheels_per_side_rear:
            if not b.ai.vehicle_disabled:
                issues.append(f'{b.name} insufficient healthy wheels but not disabled')

    # check electrical system
    if len(b.ai.batteries) > 0 and not b.ai.electrical_system_functioning and b.ai.engines_on:
        issues.append(f'{b.name} has batteries but electrical system not functioning')

#---------------------------------------------------------------------------
def check_human_primary_weapon(b, issues, world):
    '''sanity checks for human primary_weapon'''
    if b.ai.primary_weapon is None:
        # check if there are unequipped guns in inventory that could be equipped
        for item in b.ai.inventory:
            if item.is_gun and item.ai.equipper is None:
                issues.append(f'{b.name} has unequipped gun {item.name} in inventory but primary_weapon is None')
                break  # avoid multiple issues
    else:
        # primary_weapon is not None
        if b.ai.primary_weapon not in b.ai.inventory:
            issues.append(f'{b.name} primary_weapon {b.ai.primary_weapon.name} not in inventory')
        elif b.ai.primary_weapon.ai.equipper != b:
            issues.append(f'{b.name} primary_weapon {b.ai.primary_weapon.name} equipper mismatch')
        else:
            # check ammo - only if equipped correctly
            ammo_gun, ammo_inventory, _ = b.ai.check_ammo(b.ai.primary_weapon, b)
            if ammo_gun == 0 and ammo_inventory == 0 and not b.ai.primary_weapon.ai.damaged:
                # allow for damaged weapons to have no ammo
                issues.append(f'{b.name} primary_weapon {b.ai.primary_weapon.name} has no ammo and may need resupply')

#---------------------------------------------------------------------------
def run_wo_objects_check(world):
    '''sanity checks all world objects'''

    print('------------------------------------')
    print('world object check ')
    print('------------------------------------')

    for b in world.grid_manager.get_all_objects():
        issues=[]
        if b.in_world is False:
            issues.append(f'{b.name} .in_world is False')
        if b.grid_square is None:
            issues.append(f'{b.name} .grid_square is None')
        else:
            if b not in b.grid_square.wo_objects:
                issues.append(f'{b.name} not in .grid_square.wo_objects')

        if b.is_human:
            current_task = b.ai.memory.get('current_task', '')
            if current_task == 'task_vehicle_crew':
                check_task_vehicle_crew(b, issues, world)
            elif current_task == 'task_enter_vehicle':
                check_task_enter_vehicle(b, issues, world)
            elif current_task == 'task_move_to_location':
                check_task_move_to_location(b, issues, world)
            elif current_task == 'task_engage_enemy':
                check_task_engage_enemy(b, issues, world)

            # general human sanity checks
            check_human_primary_weapon(b, issues, world)

        elif b.is_vehicle:
            check_vehicle_sanity(b, issues, world)

        if len(issues)>0:
            print('----------')
            for c in issues:
                print(c)
            print('----------')


    print('------------------------------------')

#---------------------------------------------------------------------------
def start(world):
    '''entry point. starts the debug'''

    # for simplicity the debug will print out to console 

    # object counts
    run_object_counts_report(world)

    # object sanity check
    run_wo_objects_check(world)
