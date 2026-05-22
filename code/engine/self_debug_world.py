
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
    vcrew = b.ai.memory.get('task_vehicle_crew', {})
    expected_keys = [
        'vehicle_role', 'current_action', 'current_action_details', 'target',
        'calculated_turret_angle', 'engage_primary_weapon', 'engage_coaxial_weapon',
        'engage_indirect_fire', 'calculated_vehicle_angle', 'calculated_distance_to_target',
        'last_think_time', 'think_interval', 'reload_start_time', 'vehicle_order',
        'fire_missions', 'vehicle_hits'
    ]
    for key in expected_keys:
        if key not in vcrew:
            issues.append(f'{b.name} missing {key} in task_vehicle_crew memory')

    vehicle_role = vcrew.get('vehicle_role')
    if vehicle_role is None:
        issues.append(f'{b.name} vehicle_role is None in task_vehicle_crew')
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
            # check distance (crew should be at/near their vehicle)
            distance = engine.math_2d.get_distance(b.world_coords, vehicle_role.vehicle.world_coords)
            if distance > 100:
                issues.append(f'{b.name} too far from vehicle {vehicle_role.vehicle.name} ({distance:.1f} units)')



#---------------------------------------------------------------------------
def check_task_enter_vehicle(b, issues, world):
    '''sanity checks for task_enter_vehicle'''
    task_mem = b.ai.memory.get('task_enter_vehicle', {})
    for key in ('vehicle', 'vehicle_order', 'original_distance_to_vehicle'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_enter_vehicle memory')

    vehicle = task_mem.get('vehicle')
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
    task_mem = b.ai.memory.get('task_move_to_location', {})
    for key in ('destination', 'moving_object', 'last_think_time', 'think_interval'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_move_to_location memory')

    dest = task_mem.get('destination')
    if dest is not None:
        if not (isinstance(dest, (list, tuple)) and len(dest) == 2):
            issues.append(f'{b.name} destination is not a 2-element list/tuple: {dest}')
        else:
            if abs(dest[0]) > 50000 or abs(dest[1]) > 50000:
                issues.append(f'{b.name} destination out of bounds: {dest}')

    mo = task_mem.get('moving_object')
    if mo is not None:
        if mo not in world.grid_manager.get_all_objects():
            issues.append(f'{b.name} moving_object not in world objects')
        if mo.in_world is False:
            issues.append(f'{b.name} moving_object not in world')

#---------------------------------------------------------------------------
def check_task_engage_enemy(b, issues, world):
    '''sanity checks for task_engage_enemy'''
    task_mem = b.ai.memory.get('task_engage_enemy', {})
    for key in ('enemy', 'last_think_time', 'think_interval'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_engage_enemy memory')

    enemy = task_mem.get('enemy')
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
def check_task_exit_vehicle(b, issues, _world):
    '''minimal sanity for task_exit_vehicle (memory is intentionally empty)'''
    if 'task_exit_vehicle' not in b.ai.memory:
        issues.append(f'{b.name} missing task_exit_vehicle memory dict')

#---------------------------------------------------------------------------
def check_task_loot_container(b, issues, world):
    '''sanity for task_loot_container'''
    task_mem = b.ai.memory.get('task_loot_container', {})
    if 'container' not in task_mem:
        issues.append(f'{b.name} missing container in task_loot_container memory')
    container = task_mem.get('container')
    if container is not None:
        if container not in world.grid_manager.get_all_objects():
            issues.append(f'{b.name} loot container not in world objects')
        if container.in_world is False:
            issues.append(f'{b.name} loot container not in world')

#---------------------------------------------------------------------------
def check_task_medic(b, issues, world):
    '''sanity for task_medic'''
    task_mem = b.ai.memory.get('task_medic', {})
    for key in ('wounded_humans', 'current_patient'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_medic memory')
    for h in (task_mem.get('wounded_humans') or []):
        if h is not None:
            if h not in world.grid_manager.get_all_objects():
                issues.append(f'{b.name} medic target {h.name} not in world objects')
            if h.in_world is False:
                issues.append(f'{b.name} medic target {h.name} not in world')
    patient = task_mem.get('current_patient')
    if patient is not None:
        if patient not in world.grid_manager.get_all_objects():
            issues.append(f'{b.name} current_patient not in world objects')
        if patient.in_world is False:
            issues.append(f'{b.name} current_patient not in world')

#---------------------------------------------------------------------------
def check_task_mechanic(b, issues, world):
    '''sanity for task_mechanic'''
    task_mem = b.ai.memory.get('task_mechanic', {})
    for key in ('damaged_vehicles', 'current_vehicle'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_mechanic memory')
    for v in (task_mem.get('damaged_vehicles') or []):
        if v is not None:
            if v not in world.grid_manager.get_all_objects():
                issues.append(f'{b.name} mechanic target vehicle not in world objects')
            if v.in_world is False:
                issues.append(f'{b.name} mechanic target vehicle not in world')
    veh = task_mem.get('current_vehicle')
    if veh is not None:
        if veh not in world.grid_manager.get_all_objects():
            issues.append(f'{b.name} current_vehicle not in world objects')
        if veh.in_world is False:
            issues.append(f'{b.name} current_vehicle not in world')

#---------------------------------------------------------------------------
def check_task_pickup_objects(b, issues, world):
    '''sanity for task_pickup_objects'''
    task_mem = b.ai.memory.get('task_pickup_objects', {})
    if 'objects' not in task_mem:
        issues.append(f'{b.name} missing objects in task_pickup_objects memory')
    for obj in (task_mem.get('objects') or []):
        if obj is not None:
            if obj not in world.grid_manager.get_all_objects():
                issues.append(f'{b.name} pickup target not in world objects')
            if obj.in_world is False:
                issues.append(f'{b.name} pickup target not in world')

#---------------------------------------------------------------------------
def check_task_player_control(b, issues, _world):
    '''minimal sanity for task_player_control (memory intentionally minimal for player)'''
    if not b.is_player and 'task_player_control' not in b.ai.memory:
        issues.append(f'{b.name} missing task_player_control memory dict')

#---------------------------------------------------------------------------
def check_task_reload(b, issues, world):
    '''sanity for task_reload'''
    task_mem = b.ai.memory.get('task_reload', {})
    for key in ('weapon', 'reload_start_time'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_reload memory')
    weapon = task_mem.get('weapon')
    if weapon is not None:
        # weapon may be in inventory (not in grid) or world object if dropped
        if weapon not in b.ai.inventory and weapon not in world.grid_manager.get_all_objects():
            issues.append(f'{b.name} reload weapon neither in inventory nor world objects')
        if hasattr(weapon, 'in_world') and weapon.in_world is False:
            issues.append(f'{b.name} reload weapon not in world')

#---------------------------------------------------------------------------
def check_task_sit_down(b, issues, world):
    '''sanity for task_sit_down'''
    task_mem = b.ai.memory.get('task_sit_down', {})
    for key in ('status', 'furniture_object', 'sit_start_time', 'sit_duration'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_sit_down memory')
    furn = task_mem.get('furniture_object')
    if furn is not None:
        if furn not in world.grid_manager.get_all_objects():
            issues.append(f'{b.name} sit furniture not in world objects')
        if furn.in_world is False:
            issues.append(f'{b.name} sit furniture not in world')

#---------------------------------------------------------------------------
def check_task_squad_leader(b, issues, _world):
    '''sanity for task_squad_leader (orders are TacticalOrder objects, not world objs)'''
    task_mem = b.ai.memory.get('task_squad_leader', {})
    for key in ('last_think_time', 'think_interval', 'orders'):
        if key not in task_mem:
            issues.append(f'{b.name} missing {key} in task_squad_leader memory')

#---------------------------------------------------------------------------
def check_task_think(b, issues, _world):
    '''minimal sanity for task_think'''
    if 'task_think' not in b.ai.memory:
        issues.append(f'{b.name} missing task_think memory dict')

#---------------------------------------------------------------------------
def check_task_think_idle(b, issues, _world):
    '''minimal sanity for task_think_idle'''
    if 'task_think_idle' not in b.ai.memory:
        issues.append(f'{b.name} missing task_think_idle memory dict')

#---------------------------------------------------------------------------
def check_task_wait(b, issues, _world):
    '''sanity for task_wait'''
    task_mem = b.ai.memory.get('task_wait', {})
    if 'end_time' not in task_mem:
        issues.append(f'{b.name} missing end_time in task_wait memory')

#---------------------------------------------------------------------------
def check_vehicle_sanity(b, issues, world):
    '''sanity checks for vehicles'''
    # check crew
    for i, role in enumerate(b.ai.vehicle_crew):
        # CRITICAL: Check for role/human mismatch - these are the actual data integrity problems
        if role.role_occupied and role.human is None:
            issues.append(f'CRITICAL DATA ERROR: {b.name} role {role.role_name} is OCCUPIED but human is None!')
            role.role_occupied = False
        if not role.role_occupied and role.human is not None:
            issues.append(f'CRITICAL DATA ERROR: {b.name} role {role.role_name} is EMPTY but human {role.human.name} is assigned!')
            issues.append(f' Human memory dump {role.human.ai.memory}')
            if 'task_vehicle_crew' in role.human.ai.memory:
                vc = role.human.ai.memory['task_vehicle_crew']
                if vc.get('vehicle_role'):
                    issues.append(f'  Human points to role: {vc["vehicle_role"].role_name}')
                    issues.append(f'  This role is NOT in this vehicle\'s crew list!')
            role.human = None
        if role.role_occupied and role.human:
            if role.human.ai.blood_pressure<30:
                issues.append(f'{b.name} crew {role.human.name} blood pressure ({role.human.ai.blood_pressure}) low')
            if role.human not in world.grid_manager.get_all_objects():
                issues.append(f'{b.name} crew {role.human.name} not in world objects')
            if role.human.in_world is False:
                issues.append(f'{b.name} crew {role.human.name} not in world')
            if role.human.ai.memory.get('current_task') != 'task_vehicle_crew':
                issues.append(f"{b.name} crew {role.human.name} memory[current_task] is {role.human.ai.memory['current_task']} not task_vehicle_crew")
            if 'vehicle_role' not in role.human.ai.memory.get('task_vehicle_crew', {}):
                issues.append(f'{b.name} crew {role.human.name} missing vehicle_role in memory')
            else:
                if role.human.ai.memory['task_vehicle_crew']['vehicle_role'] != role:
                    issues.append(f'{b.name} crew {role.human.name} vehicle_role mismatch')
                    role.human = None
                    role.role_occupied = False



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

# ---------------------------------------------------------------------------
def check_human_primary_weapon(b, issues, _world):
    '''sanity checks for human primary_weapon'''
    if b.ai.primary_weapon is None:
        # check if there are unequipped guns in inventory that could be equipped
        for item in b.ai.inventory:
            if item.is_gun and item.ai.equipper is None:
                issues.append(f'{b.name} has unequipped gun {item.name} in inventory but primary_weapon is None')
                break  # avoid multiple issues
    else:
        # primary_weapon is not None, but check if it has a name attribute
        try:
            weapon_name = b.ai.primary_weapon.name
        except AttributeError:
            weapon_name = b.ai.primary_weapon

        # primary_weapon is not None
        if b.ai.primary_weapon not in b.ai.inventory:
            issues.append(f'{b.name} primary_weapon {weapon_name} not in inventory')
        elif b.ai.primary_weapon.ai.equipper != b:
            issues.append(f'{b.name} primary_weapon {weapon_name} equipper mismatch')
        else:
            # check ammo - only if equipped correctly
            try:
                ammo_gun, ammo_inventory, _ = b.ai.check_ammo(b.ai.primary_weapon, b)
                if ammo_gun == 0 and ammo_inventory == 0 and not b.ai.primary_weapon.ai.damaged:
                    # allow for damaged weapons to have no ammo
                    issues.append(f'{b.name} primary_weapon {weapon_name} has no ammo and may need resupply')
            except Exception as e:
                issues.append(f'{b.name} primary_weapon check failed: {e}')

# ---------------------------------------------------------------------------
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
            # task -> checker function map (keeps dispatch clean & matches AI task_map pattern)
            task_checkers = {
                'task_vehicle_crew': check_task_vehicle_crew,
                'task_enter_vehicle': check_task_enter_vehicle,
                'task_move_to_location': check_task_move_to_location,
                'task_engage_enemy': check_task_engage_enemy,
                'task_exit_vehicle': check_task_exit_vehicle,
                'task_loot_container': check_task_loot_container,
                'task_medic': check_task_medic,
                'task_mechanic': check_task_mechanic,
                'task_pickup_objects': check_task_pickup_objects,
                'task_player_control': check_task_player_control,
                'task_reload': check_task_reload,
                'task_sit_down': check_task_sit_down,
                'task_squad_leader': check_task_squad_leader,
                'task_think': check_task_think,
                'task_think_idle': check_task_think_idle,
                'task_wait': check_task_wait,
            }
            checker = task_checkers.get(current_task)
            if checker:
                checker(b, issues, world)

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
