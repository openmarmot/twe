
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : the ai_human code for decisions when in vehicles
'''

#import built in modules
import random
import copy

#import custom packages
import engine.math_2d
import engine.world_builder
import engine.log
import engine.penetration_calculator
from engine.vehicle_order import VehicleOrder
from engine.tactical_order import TacticalOrder
#import engine.global_exchange_rates

class AIHumanVehicle():
    def __init__(self, owner):
        self.owner=owner

        # distance tuning
        # when a vehicle is < this distance to a target it is considered arrived
        self.vehicle_arrival_distance=150

        # -- firing pattern stuff
        # burst control keeps ai from shooting continuous streams
        self.current_burst=0 # int number of bullets shot in current burst
        self.max_burst=5

    #---------------------------------------------------------------------------
    def action_vehicle_driver(self):
        ''' the action the driver is taking when not thinking'''
        # some default values
        vehicle = self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        vehicle.ai.throttle = 0
        vehicle.ai.brake_power = 1

        if self.owner.ai.memory['task_vehicle_crew']['current_action'] == 'driving':
            calculated_distance = self.owner.ai.memory['task_vehicle_crew']['calculated_distance_to_target']
            calculated_vehicle_angle = self.owner.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']
            
            # initial throttle settings
            if calculated_distance < 150:
                # apply brakes. bot will only exit when speed is zero
                # note this number should be < the minimum distance to jump out
                # or you can end up with drivers stuck in the vehicle if they slow down fast
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
            elif calculated_distance < 300:
                vehicle.ai.throttle = 0.5
                vehicle.ai.brake_power = 0
            else:
                vehicle.ai.throttle = 1
                vehicle.ai.brake_power = 0

            # Normalize both angles to [0, 360)
            current_angle = engine.math_2d.get_normalized_angle(vehicle.rotation_angle)
            desired_angle = engine.math_2d.get_normalized_angle(calculated_vehicle_angle)
            
            # Compute shortest signed difference (-180 to +180)
            diff = (desired_angle - current_angle + 180) % 360 - 180
            
            # If close enough, snap to exact angle and neutral steering
            if abs(diff) <= 4:  # Adjusted threshold to match original logic
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle = desired_angle
                vehicle.ai.update_heading()
            else:
                # Steer in the direction of the shortest diff
                if diff > 0:
                    vehicle.ai.handle_steer_left()  # Assuming this increases angle
                    # helps turn faster
                    if vehicle.ai.throttle > 0.5:
                        vehicle.ai.throttle = 0.5
                else:
                    vehicle.ai.handle_steer_right()  # Assuming this decreases angle
                    # helps turn faster
                    if vehicle.ai.throttle > 0.5:
                        vehicle.ai.throttle = 0.5
            
            return
        
        if self.owner.ai.memory['task_vehicle_crew']['current_action'] == 'rotating':
            # rotating in place with minimal movement
            # throttle + brake seems to be working here fairly well

            calculated_vehicle_angle = self.owner.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']

            if vehicle.ai.current_speed > 10:
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
            else:
                vehicle.ai.throttle = 0.2
                vehicle.ai.brake_power = 1

            # Normalize both angles to [0, 360)
            current_angle = engine.math_2d.get_normalized_angle(vehicle.rotation_angle)
            desired_angle = engine.math_2d.get_normalized_angle(calculated_vehicle_angle)
            
            # Compute shortest signed difference (-180 to +180)
            diff = (desired_angle - current_angle + 180) % 360 - 180
            
            # If close enough, snap to exact angle and stop
            if abs(diff) <= 6:  # Adjusted threshold to match original logic
                vehicle.ai.handle_steer_neutral()
                vehicle.rotation_angle = desired_angle
                vehicle.ai.update_heading()
                vehicle.ai.throttle = 0
                vehicle.ai.brake_power = 1
                # this action is now done
                self.owner.ai.memory['task_vehicle_crew']['current_action'] = 'idle'
            else:
                # Rotate in the direction of the shortest diff
                if diff > 0:
                    vehicle.ai.handle_steer_left()
                else:
                    vehicle.ai.handle_steer_right()


    #---------------------------------------------------------------------------
    def action_vehicle_gunner_engage_target(self):
        # this is the action the vehicle gunner takes when it is NOT thinking
        # and has a target that is not None
        target=self.owner.ai.memory['task_vehicle_crew']['target']
        # the computed lead on the target
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret

        # rotate turret towards target. true if rotation matches
        if self.rotate_turret(turret,self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']):
            if target.is_human:
                if target.ai.blood_pressure<1:
                    self.owner.ai.memory['task_vehicle_crew']['target']=None
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                    return
            if target.is_vehicle:
                if target.ai.check_if_vehicle_is_occupied() is False or target.ai.vehicle_disabled:
                    self.owner.ai.memory['task_vehicle_crew']['target']=None
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                    return

            # handle bursts and fire weapon
            if self.owner.ai.memory['task_vehicle_crew']['engage_primary_weapon']:
                if turret.ai.handle_fire():
                    self.current_burst+=1

            if self.owner.ai.memory['task_vehicle_crew']['engage_coaxial_weapon']:
                if turret.ai.handle_fire_coax():
                    self.current_burst+=1

            if self.current_burst>self.max_burst:
                # randomize burst length a little. this should create a random burst length from 3 to the max burst
                self.current_burst=random.randint(0,self.max_burst-3)

                # prevents the next burst from being sent at the same target while bullets are in flight
                # less of an issue with vehicle targets
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'

    #---------------------------------------------------------------------------
    def calculate_turret_aim(self,turret,target,weapon):
        '''calculates the correct turret angle to hit a target'''

        # this is where we should be applying the majority of the aim adjustments

        # target : world_object
        # turret : world_object with ai_turret

        aim_coords=target.world_coords
        # guess how long it will take for the bullet to arrive
        distance=engine.math_2d.get_distance(turret.world_coords,target.world_coords)

        # - determine adjustment - 
        adjust_max=0
        adjust_max+=weapon.ai.mechanical_accuracy

        if self.owner.ai.blood_pressure<100:
            adjust_max+=1
        if self.owner.ai.blood_pressure<50:
            adjust_max+=10

        if distance>1000:
            adjust_max+=1
        if distance>2000:
            adjust_max+=2
        if distance>3000:
            adjust_max+=5
        if distance>3500:
            adjust_max+=5

        if adjust_max<0:
            adjust_max=0

        # final results
        aim_coords=[aim_coords[0]+random.uniform(-adjust_max,adjust_max),aim_coords[1]+random.uniform(-adjust_max,adjust_max)]

         # we want the projectile to collide so aim point will be a bit past it
        weapon.ai.calculated_range=distance+random.randint(0,500)
        time_passed=distance/weapon.ai.muzzle_velocity
        if target.is_vehicle:

            if target.ai.current_speed>0:
                aim_coords=engine.math_2d.moveAlongVector(target.ai.current_speed,aim_coords,target.heading,time_passed)

        if target.is_human:
            if target.ai.memory['current_task']=='task_vehicle_crew':
                vehicle=target.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
                if vehicle.ai.current_speed>0:
                    aim_coords=engine.math_2d.moveAlongVector(vehicle.ai.current_speed,aim_coords,vehicle.heading,time_passed)
            else:
                if target.ai.memory['current_task']=='task_move_to_location':
                    destination=target.ai.memory['task_move_to_location']['destination']
                    aim_coords=engine.math_2d.moveTowardsTarget(target.ai.get_calculated_speed(),aim_coords,destination,time_passed)

        

        self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']=engine.math_2d.get_rotation(turret.world_coords,aim_coords)

    #---------------------------------------------------------------------------
    def check_vehicle_turret_rotation_real_angle(self,rotation_angle,turret):
        '''checks whether a vehicle turret can rotate to match a world angle'''
        # this checks whether a turret can rotate to match a angle given the turrets restraints
        # this is here because it is a human dead reckoning thing, not a function of the turret itself
        # returns true if the turret can rotate to this angle
        # reeturns false if it cannot
        angle_ok=False
        if rotation_angle>turret.ai.vehicle.rotation_angle+turret.ai.rotation_range[0]:
            if rotation_angle<turret.ai.vehicle.rotation_angle+turret.ai.rotation_range[1]:
                angle_ok=True

        # this also needs to check the turrets starting rotation.
        # for example, some turrets may face forward, some may face backward 

        return angle_ok
    
    #---------------------------------------------------------------------------
    def rotate_turret(self, turret, desired_angle):
        '''rotates a turret. returns True/False as to whether the turret is at the desired angle'''
        
        # Normalize both angles to [0, 360)
        current_angle = engine.math_2d.get_normalized_angle(turret.rotation_angle)
        desired_angle = engine.math_2d.get_normalized_angle(desired_angle)
        
        # Compute shortest signed difference (-180 to +180)
        diff = (desired_angle - current_angle + 180) % 360 - 180
        
        # If close enough, snap to exact angle and stop
        if abs(diff) <= 2:  # Adjust threshold if needed for precision
            turret.rotation_angle = desired_angle
            turret.ai.rotation_change = 0
            return True
        
        # Rotate in the direction of the shortest diff
        # Assumption: positive rotation_change increases angle (e.g., clockwise); adjust signs if your coord system is counterclockwise
        if diff > 0:
            turret.ai.handle_rotate_left()  # Increases angle
        else:
            turret.ai.handle_rotate_right()  # Decreases angle
        
        return False
    
    #---------------------------------------------------------------------------
    def think_vehicle_hit(self):
        '''vehicle occupant reacts to the vehicle being hit'''
        # for this to be called the vehicle_hits list is not empty
        
        # set it to whatever the first one is
        important_hit=self.owner.ai.memory['task_vehicle_crew']['vehicle_hits'][0]

        # check if anything is more important
        for hit in self.owner.ai.memory['task_vehicle_crew']['vehicle_hits']:
            if hit.penetrated:
                important_hit=hit
                break

            if hit.projectile_shooter:
                if hit.projectile_shooter.is_turret:
                    important_hit=hit
        
        # we can now clear the list
        self.owner.ai.memory['task_vehicle_crew']['vehicle_hits']=[]

        role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']

        if important_hit.penetrated:
            self.owner.ai.morale-=10
            if self.owner.ai.morale_check() is False:
                self.owner.ai.speak('The vehicle is hit! Bail out!!')
                self.owner.ai.switch_task_exit_vehicle()
                return
            
            if role.is_gunner:
                if hit.projectile_shooter:
                    if hit.projectile_shooter.is_turret:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter.ai.vehicle
                    else:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter
                    return
            if role.is_passenger:
                # i feel that passengers should probably bail if there is a penetration 
                # really no reason for them to do anything else
                self.owner.ai.speak('The vehicle is hit! Bail out!!')
                self.owner.ai.switch_task_exit_vehicle()
                return
        else:
            # not a penetration, so less of a reaction 

            if role.is_gunner:
                if hit.projectile_shooter:
                    if hit.projectile_shooter.is_turret:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter.ai.vehicle
                        return
                    # only engage humans if we aren't doing anything else
                    if self.owner.ai.memory['task_vehicle_crew']['target'] is None:
                        self.owner.ai.memory['task_vehicle_crew']['target']=hit.projectile_shooter
                        return
                    
            # maybe add some morale damage?



    #---------------------------------------------------------------------------
    def think_vehicle_role_driver(self):
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

        # precheck to make sure we aren't in combat 
        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied and role.is_gunner:
                if role.turret.ai.primary_weapon:
                    current_action=role.human.ai.memory['task_vehicle_crew']['current_action']
                    if 'reloading' in current_action:
                        self.owner.ai.memory['task_vehicle_crew']['current_action']='waiting on crew to finish reloading'
                        vehicle.ai.brake_power=1
                        vehicle.ai.throttle=0
                        # wait to think for a bit so we don't end up doing something else immediately
                        self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
                        return
                    if 'Engaging' in current_action:
                        self.owner.ai.memory['task_vehicle_crew']['current_action']='waiting on crew to finish engagement'
                        vehicle.ai.brake_power=1
                        vehicle.ai.throttle=0
                        # wait to think for a bit so we don't end up doing something else immediately
                        self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
                        return
                    if 'jam' in current_action:
                        self.owner.ai.memory['task_vehicle_crew']['current_action']='waiting on gunner to finish clearing weapon jam'
                        vehicle.ai.brake_power=1
                        vehicle.ai.throttle=0
                        # wait to think for a bit so we don't end up doing something else immediately
                        self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
                        return
                    if current_action=='Waiting for driver to rotate the vehicle':
                        target=role.human.ai.memory['task_vehicle_crew']['target']
                        if target is not None:
                            
                            # catch out of fuel 
                            current_fuel,max_fuel=vehicle.ai.read_fuel_gauge()
                            if current_fuel==0 and max_fuel>0:
                                engine.log.add_data('warn',f'ai_human_vehicle.think_vehicle_role_driver waiting for driver {self.owner.name}  to rotate {vehicle.name} and out of fuel, marking vehicle disabled',True)
                                vehicle.ai.vehicle_disabled=True
                                return


                            rotation_required=engine.math_2d.get_rotation(vehicle.world_coords,target.world_coords)
                            v=vehicle.rotation_angle
                            if rotation_required>v-1 and rotation_required<v+1:
                                # we are close enough
                                self.owner.ai.memory['task_vehicle_crew']['current_action']='waiting'
                                vehicle.ai.brake_power=1
                                vehicle.ai.throttle=0
                                # wait to think for a bit so we don't end up doing something else immediately
                                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
                                return
                            #default
                            self.owner.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']=rotation_required
                            self.owner.ai.memory['task_vehicle_crew']['current_action']='rotating'
                            return
                    if current_action=='Waiting for driver to close distance with target':
                        target=role.human.ai.memory['task_vehicle_crew']['target']
                        if target is not None:
                            need_vehicle_order=False
                            if self.owner.ai.memory['task_vehicle_crew']['vehicle_order'] is None:
                                need_vehicle_order=True
                            else:
                                if self.owner.ai.memory['task_vehicle_crew']['vehicle_order'].order_close_with_enemy is False:
                                    need_vehicle_order=True
                            # ensuring we only do this once
                            if need_vehicle_order:
                                vehicle_order=VehicleOrder()
                                vehicle_order.order_close_with_enemy=True
                                vehicle_order.world_coords=copy.copy(target.world_coords)
                                if vehicle.ai.is_transport:
                                    vehicle_order.exit_vehicle_when_finished=True
                                self.owner.ai.memory['task_vehicle_crew']['vehicle_order']=vehicle_order
        
        # next lets check if anyone is trying to get in 
        if vehicle.ai.check_if_vehicle_is_full() is False:
            new_passengers=False
            for b in self.owner.ai.squad.faction_tactical.allied_humans:
                if 'task_enter_vehicle' in b.ai.memory:
                    if vehicle is b.ai.memory['task_enter_vehicle']['vehicle']:
                        new_passengers=True
                        break

            if new_passengers:
                # wait for new passengers
                # no need to check this again for a bit
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.8,1)
                vehicle.ai.brake_power=1
                vehicle.ai.throttle=0
                self.owner.ai.memory['task_vehicle_crew']['current_action']='waiting for passengers'
                return
        
        # lets check our orders
        if self.owner.ai.memory['task_vehicle_crew']['vehicle_order'] is not None:
            self.think_vehicle_role_driver_vehicle_order()
            return
        else:
            # does anyone else have any orders?
            for role in vehicle.ai.vehicle_crew:
                if role.role_occupied:
                    if role.human.ai.memory['task_vehicle_crew']['vehicle_order'] is not None:
                        # grab their order
                        self.owner.ai.memory['task_vehicle_crew']['vehicle_order']=role.human.ai.memory['task_vehicle_crew']['vehicle_order']
                        role.human.ai.memory['task_vehicle_crew']['vehicle_order']=None
                        return

        # should be not very likely to get this far.
        
        # how far are we from the squad leader?
        if self.owner.ai.squad.squad_leader is not None:
            distance_to_squad_lead=engine.math_2d.get_distance(self.owner.world_coords,self.owner.ai.squad.squad_leader.world_coords)
            if distance_to_squad_lead > 300:
                vehicle_order=VehicleOrder()
                vehicle_order.order_drive_to_coords=True
                vehicle_order.world_coords=copy.copy(self.owner.ai.squad.squad_leader.world_coords)
                if vehicle.ai.is_transport:
                    vehicle_order.exit_vehicle_when_finished=True
                self.owner.ai.memory['task_vehicle_crew']['vehicle_order']=vehicle_order
                return
        
        # default behavior after everything else 
        # no orders 
        # close to squad lead
        self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting at destination'
        vehicle.ai.brake_power=1
        vehicle.ai.throttle=0

        # should probably make a decision about jumping out at this point
        if vehicle.ai.is_transport:
            # check if any squad leads are in the crew. if so they will figure out what to do
            crew_squad_lead=False
            for role in vehicle.ai.vehicle_crew:
                if role.role_occupied:
                    if role.human.ai.squad.squad_leader==role.human:
                        crew_squad_lead=True
                        break
            if crew_squad_lead is False:
                # no squad lead so no new vehicle orders unless if the squad lead moves
                # might as well get out for a bit

                # this might cause issues if the crew has conditions that cause them 
                # to re-enter the vehicle 
                

                for role in vehicle.ai.vehicle_crew:
                    if role.role_occupied:
                        role.human.ai.switch_task_exit_vehicle()

    #---------------------------------------------------------------------------
    def think_vehicle_role_driver_drive_to_destination(self,destination,distance):
        '''perform actions necessary to start driving somewhere'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

        # temp for testing
        if vehicle.ai.vehicle_disabled:
            print(f'debug !! vehicle {vehicle.name} is already disabled!!')

        rotation=engine.math_2d.get_rotation(vehicle.world_coords,destination)
        self.owner.ai.memory['task_vehicle_crew']['current_action']='driving'
        self.owner.ai.memory['task_vehicle_crew']['calculated_distance_to_target']=distance
        self.owner.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']=rotation
        # turn engines on
        # could do smarter checks here once engines have more stats
        need_start=False
        for b in vehicle.ai.engines:
            if b.ai.engine_on is False:
                need_start=True
                break
        if need_start:
            current_fuel,max_fuel=vehicle.ai.read_fuel_gauge()
            if current_fuel>0:
                vehicle.ai.handle_start_engines()
            else:
                # there might be some cases where this happens and we should have turned the engine on anyways (some engines don't use fuel)
                if max_fuel==0:
                    engine.log.add_data('warn',f'ai_human_vehicle think_vehicle_role_driver_drive_to_destination max_fuel==0 for vehicle {vehicle.name}',True)

                # out of fuel.
                # disable the vehicle for now. in the future we will want to try and get fuel and refuel
                engine.log.add_data('warn',f'ai_human_vehicle.think_vehicle_role_driver_drive_to_destination out of fuel. driver {self.owner.name} vehicle {vehicle.name} marking vehicle disabled',True)
                vehicle.ai.vehicle_disabled=True
    #---------------------------------------------------------------------------
    def think_vehicle_role_driver_vehicle_order(self):
        '''think about the drivers current vehicle order'''
        order=self.owner.ai.memory['task_vehicle_crew']['vehicle_order']
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        if order.order_drive_to_coords or order.order_close_with_enemy:
            distance=engine.math_2d.get_distance(vehicle.world_coords,order.world_coords)
            if distance<self.vehicle_arrival_distance and vehicle.ai.current_speed<10:
                # we have arrived and can delete the order.
                self.owner.ai.memory['task_vehicle_crew']['current_action']='waiting'
                vehicle.ai.brake_power=1
                vehicle.ai.throttle=0

                if order.exit_vehicle_when_finished:
                    if vehicle.ai.is_transport:
                        for role in vehicle.ai.vehicle_crew:
                            if role.role_occupied:
                                role.human.ai.switch_task_exit_vehicle()
                                # this will also clear out any vehicle_orders they had

                # delete the order
                self.owner.ai.memory['task_vehicle_crew']['vehicle_order']=None

                return
            #default
            self.think_vehicle_role_driver_drive_to_destination(order.world_coords,distance)
            return
        if order.order_tow_object:
            # future 
            return

    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner(self):
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret

        # handle the reloading action
        if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading primary weapon':
            if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
            > turret.ai.primary_weapon_reload_speed):
                self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                self.think_vehicle_role_gunner_reload(turret.ai.primary_weapon)
            else:
                return
        if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading coax gun':
            if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
            > turret.ai.coaxial_weapon_reload_speed):
                self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                self.think_vehicle_role_gunner_reload(turret.ai.coaxial_weapon)
                
            else:
                return    

        out_of_ammo_primary=False
        out_of_ammo_coax=False
        turret_jammed=turret.ai.turret_jammed
        weapons_damaged=False
        weapons_jammed=False

        # check main gun ammo
        ammo_gun,ammo_inventory,magazine_count=self.owner.ai.check_ammo(turret.ai.primary_weapon,vehicle)
        if ammo_gun==0:
            if ammo_inventory>0:
                # start the reload process
                self.owner.ai.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                self.owner.ai.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                return
            else:
                out_of_ammo_primary=True

        # check coax ammo
        if turret.ai.coaxial_weapon is not None:
            ammo_gun,ammo_inventory,magazine_count=self.owner.ai.check_ammo(turret.ai.coaxial_weapon,vehicle)
            if ammo_gun==0:
                if ammo_inventory>0:
                    # start the reload process
                    self.owner.ai.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='reloading coax gun'
                    self.owner.ai.memory['task_vehicle_crew']['target']=None
                    return
                else:
                    out_of_ammo_coax=True
        else:
            out_of_ammo_coax=True

        # check weapons 
        if turret.ai.primary_weapon:
            if turret.ai.primary_weapon.ai.damaged:
                weapons_damaged=True
            if turret.ai.primary_weapon.ai.action_jammed:
                weapons_jammed=True
        if turret.ai.coaxial_weapon:
            if turret.ai.coaxial_weapon.ai.damaged:
                # don't want this because it soft locks the gunner
                #weapons_damaged=True
                # do this instead which will prevent engaging with the coax, but will still allow primary weapon engagement
                out_of_ammo_coax=True
            if turret.ai.coaxial_weapon.ai.action_jammed:
                weapons_jammed=True

        if out_of_ammo_coax and out_of_ammo_primary:
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Out of Ammo'
            self.owner.ai.memory['task_vehicle_crew']['target']=None
            return
        
        if turret_jammed:
            # # if this was the primary turret the vehicle will be marked disabled.
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Turret Jammed'
            self.owner.ai.memory['task_vehicle_crew']['target']=None
            return

        # need to figure out what we do if anything for a damaged coax 
        if weapons_damaged:
            # if this was the primary weapon in a primary turret the vehicle will be marked disabled (if not a transport)
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Weapons Damaged'
            self.owner.ai.memory['task_vehicle_crew']['target']=None
            return
        
        if weapons_jammed:
            # this we can fix ourselves
            #if we are already in this state then consider it fixed 
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='Clearing weapon jam':
                if turret.ai.primary_weapon:
                    if turret.ai.primary_weapon.ai.action_jammed:
                        self.owner.ai.speak('fixing jammed gun')
                        turret.ai.primary_weapon.ai.action_jammed=False
                if turret.ai.coaxial_weapon:
                    if turret.ai.coaxial_weapon.ai.action_jammed:
                        self.owner.ai.speak('fixing jammed gun')
                        turret.ai.coaxial_weapon.ai.action_jammed=False
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                # this should then flow through to getting a new target
            else:
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Clearing weapon jam'
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                # wait for a bit to simulate fixing.
                # on the next loop it will be fixed
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(25,45)
                return

        if self.owner.ai.memory['task_vehicle_crew']['target'] is None:
            target=None
            if turret.ai.primary_weapon.ai.use_antitank:
                #prioritize vehicles
                target=self.owner.ai.get_target_vehicle(turret.ai.primary_weapon.ai.range)
                if target is None:
                    target=self.owner.ai.get_target_human(turret.ai.primary_weapon.ai.range)
            else:
                # prioritize humans 
                target=self.owner.ai.get_target_human(turret.ai.primary_weapon.ai.range)
                if target is None:
                    target=self.owner.ai.get_target_vehicle(turret.ai.primary_weapon.ai.range)
            if target is not None:
                self.owner.ai.memory['task_vehicle_crew']['target']=target

        # we have a target, lets think about it in more detail
        if self.owner.ai.memory['task_vehicle_crew']['target'] is not None:
            self.think_vehicle_role_gunner_examine_target(out_of_ammo_primary,out_of_ammo_coax)
                
    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner_examine_target(self,out_of_ammo_primary,out_of_ammo_coax):
        '''thinking about the current target after other things have been thought about'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret
        target=self.owner.ai.memory['task_vehicle_crew']['target']

        # check whether target is still a threat
        if target.is_human:
            if target.ai.blood_pressure<1:
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                return
        elif target.is_vehicle:
            if target.ai.check_if_vehicle_is_occupied() is False or target.ai.vehicle_disabled:
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
                return

        # check rotation
        rotation_angle=engine.math_2d.get_rotation(self.owner.world_coords,target.world_coords)
        rotation_check=self.check_vehicle_turret_rotation_real_angle(rotation_angle,turret)
        
        # check engagement for each weapon
        engage_primary=False
        engage_primary_reason=''
        engage_coaxial=False
        engage_coaxial_reason=''
        if out_of_ammo_primary is False:
            engage_primary,engage_primary_reason=self.owner.ai.calculate_engagement(turret.ai.primary_weapon,target)

            # this is necessary to force a reload if we are
            # trying to engage a vehicle with HE and have compatible AT in the inventory
            # otherwise the gunner will just drop all vehicle targets because he can't pen
            if engage_primary is False and target.is_vehicle:
                if engage_primary_reason=='':
                    # do we have HE loaded and do we have AT available?
                    if turret.ai.primary_weapon.ai.magazine:
                        if turret.ai.primary_weapon.ai.magazine.ai.use_antitank is False:
                            for m in vehicle.ai.ammo_rack:
                                if turret.ai.primary_weapon.world_builder_identity in m.ai.compatible_guns:
                                    if len(m.ai.projectiles)>0:
                                        if m.ai.use_antitank:
                                            if random.randint(0,1)==0:
                                                # fire to clear the shell out 
                                                return
                                            else:
                                                #reload to clear the shell out
                                            # start the reload process
                                                self.owner.ai.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                                                self.owner.ai.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                                                print(f'reloading {turret.ai.primary_weapon.name} because engaging vehicle and HE loaded')
                                                return
                elif engage_primary_reason=='need to get closer to penetrate':
                    if turret.ai.primary_turret:
                        # wait for a couple seconds before rechecking
                        self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.5,1)
                        self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for driver to close distance with target'
                        return
            
            # if we can't pen occasionally send a round out anyways. 
            if engage_primary is False and engage_primary_reason=='':
                if random.randint(0,4)==0:
                    engage_primary=True

            # possibly should also check if we are engaging a soft skinned vehicle with AT
                
        # out_of_ammo_coax will be true if there is no coax, or the coax is damaged
        if out_of_ammo_coax is False:
            engage_coaxial,engage_coaxial_reason=self.owner.ai.calculate_engagement(turret.ai.coaxial_weapon,target)

        if rotation_check:

                if engage_primary:
                    
                    if engage_coaxial:
                        if target.is_human:
                            # don't waste the main gun shot
                            engage_primary=False
                    else:
                        if target.is_human:
                            # only use AP mag 
                            if turret.ai.primary_weapon.ai.magazine:
                                if turret.ai.primary_weapon.ai.magazine.ai.use_antipersonnel==False:
                                    engage_primary=False

                # save the engagement commands for the gunner actions
                self.owner.ai.memory['task_vehicle_crew']['engage_primary_weapon']=engage_primary
                self.owner.ai.memory['task_vehicle_crew']['engage_coaxial_weapon']=engage_coaxial

                if engage_primary:
                    self.calculate_turret_aim(turret,target,turret.ai.primary_weapon)
                    target_name=target.name
                    if target.is_human:
                        target_name='soldiers'
                    self.owner.ai.memory['task_vehicle_crew']['current_action']=f'Engaging {target_name}'
                    return
                if engage_coaxial:
                    self.calculate_turret_aim(turret,target,turret.ai.coaxial_weapon)
                    target_name=target.name
                    if target.is_human:
                        target_name='soldiers'
                    self.owner.ai.memory['task_vehicle_crew']['current_action']=f'Engaging {target_name}'
                    return
        

        # - results: rotation issue
        if rotation_check is False:
            # lets only ask to rotate if we are the main turret
            if turret.ai.primary_turret:
                if engage_primary or engage_coaxial:
                    # check if there is a driver
                    # note this should be fixed in the future. we shouldn't assume driver is in position 0 
                    if vehicle.ai.vehicle_crew[0].is_driver and vehicle.ai.vehicle_crew[0].role_occupied:
                    # ask the driver to rotate towards the target
                        if target.is_vehicle or random.randint(0,1)==1:

                            # wait for a couple seconds before rechecking
                            self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.5,5)
                            self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for driver to rotate the vehicle'
                            return


        # default
        self.owner.ai.memory['task_vehicle_crew']['target']=None
        self.owner.ai.memory['task_vehicle_crew']['current_action']='Scanning for targets'
            
    #---------------------------------------------------------------------------
    def think_vehicle_role_gunner_reload(self,weapon):
        '''think about how we want to reload'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret
        target=self.owner.ai.memory['task_vehicle_crew']['target']
        self.owner.ai.memory['task_vehicle_crew']['current_action']='none'

        for_at=[]
        for_ap=[]
        for_both=[]

        # ammo rack
        for m in vehicle.ai.ammo_rack:
            if m.is_gun_magazine:
                if weapon.world_builder_identity in m.ai.compatible_guns:
                    if len(m.ai.projectiles)>0:
                        if m.ai.use_antitank and m.ai.use_antipersonnel:
                            for_both.append(m)
                        elif m.ai.use_antitank:
                            for_at.append(m)
                        elif m.ai.use_antipersonnel:
                            for_ap.append(m)
                        else:
                            engine.log.add_data('error',f'ai_human.think_vehicle_role_gunner_reload magazine {m.name} unknown use',True)

        for m in vehicle.ai.inventory:
            if m.is_gun_magazine:
                if weapon.world_builder_identity in m.ai.compatible_guns:
                    if len(m.ai.projectiles)>0:
                        if m.ai.use_antitank and m.ai.use_antipersonnel:
                            for_both.append(m)
                        elif m.ai.use_antitank:
                            for_at.append(m)
                        elif m.ai.use_antipersonnel:
                            for_ap.append(m)
                        else:
                            engine.log.add_data('error',f'ai_human.think_vehicle_role_gunner_reload magazine {m.name} unknown use',True)

        new_magazine=None
        prefer_at=False
        prefer_ap=False

        if len(for_both)>0:
            new_magazine=for_both[0]
        else:
            if target is None:
                # could check if vehicles are near
                if len(self.owner.ai.near_vehicle_targets)>0 or len(self.owner.ai.mid_vehicle_targets)>0 or len(self.owner.ai.far_vehicle_targets)>0:
                    prefer_at=True
                elif len(self.owner.ai.near_human_targets)>0:
                    prefer_ap=True

            else:
                if target.is_vehicle:
                    prefer_at=True
                else:
                    prefer_ap=True

        if prefer_at and len(for_at)>0:
            new_magazine=for_at[0]
        
        if prefer_ap and len(for_ap)>0:
            new_magazine=for_ap[0]

        #print(f'{vehicle.name} {weapon.name} AT:{len(for_at)}, AP: {len(for_ap)}, BOTH: {len(for_both)}')

        reload_success=self.owner.ai.reload_weapon(weapon,vehicle,new_magazine)
        if reload_success is False:
            engine.log.add_data('Error','think_vehicle_role_gunner reload failed',True)

    #---------------------------------------------------------------------------
    def think_vehicle_role_indirect_gunner(self):
        '''think vehicle role indirect fire gunner'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        turret=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].turret

        # handle the reloading action
        if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading primary weapon':
            if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
            > turret.ai.primary_weapon_reload_speed):
                self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                self.think_vehicle_role_gunner_reload(turret.ai.primary_weapon)
            else:
                return

        # check main gun ammo
        ammo_gun,ammo_inventory,magazine_count=self.owner.ai.check_ammo(turret.ai.primary_weapon,vehicle)
        if ammo_gun==0:
            if ammo_inventory>0:
                # start the reload process
                self.owner.ai.memory['task_vehicle_crew']['reload_start_time']=self.owner.world.world_seconds
                self.owner.ai.memory['task_vehicle_crew']['current_action']='reloading primary weapon'
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                return
            else:
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Out of ammo'
                return
        
        if turret.ai.primary_weapon.ai.action_jammed:
            # this we can fix ourselves
            #if we are already in this state then consider it fixed 
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='Clearing weapon jam':
                if turret.ai.primary_weapon:
                    if turret.ai.primary_weapon.ai.action_jammed:
                        self.owner.ai.speak('fixing jammed gun')
                        turret.ai.primary_weapon.ai.action_jammed=False
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Waiting for fire mission'
                return
            else:
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Clearing weapon jam'
                self.owner.ai.memory['task_vehicle_crew']['target']=None
                # wait for a bit to simulate fixing.
                # on the next loop it will be fixed
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(25,45)
                return
            
        # if we got this far we have ammo, and the weapon is functional 
        
        # note this is unfinished


    #---------------------------------------------------------------------------
    def think_vehicle_role_passenger(self):
        '''think.. as a passenger'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle


        if len(self.owner.ai.near_human_targets)>0:
            # check if we should be worried about small arms fire
            # near targets will absolutely chew up a unarmored vehicle

            # kind of a hack. left and right are likely symetric so its a good
            # general guess
            # but only jump out if the vehicle is going slow. otherwise it might get away 
            if vehicle.ai.current_speed<20 and vehicle.ai.passenger_compartment_armor['left'][0]<5:
                self.owner.ai.switch_task_exit_vehicle()

    #---------------------------------------------------------------------------
    def think_vehicle_role_radio_operator(self):
        # note radio.ai.radio_operator set by switch_task_vehicle_crew
        # not a ton that we really need to do here atm

        # !! radio specific stuff should be handled under a ai_human role so that humans with 
        # radios who are not in vehicles can also call it

        vehicle_role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']
        vehicle=vehicle_role.vehicle
        radio=vehicle.ai.radio

        if radio is None:

            # should we try to do something else?
            return
            
        else:
            # gunner also uses this, do not want to over write 
            if vehicle_role.is_gunner is False:
                self.owner.ai.memory['task_vehicle_crew']['current_action']='Beep boop. operating the radio'
            if radio.ai.power_on is False:
                radio.ai.current_frequency=self.owner.ai.squad.faction_tactical.radio_frequency
                radio.ai.turn_power_on()

                # should double check here that this worked.
                # but what are the failure conditions?
                # - bad battery 
                # - no battery?
            else:
                # check the frequency
                if radio.ai.current_frequency!=self.owner.ai.squad.faction_tactical.radio_frequency:
                    radio.ai.current_frequency=self.owner.ai.squad.faction_tactical.radio_frequency
                    # this is needed to reset frequency with world_radio
                    radio.ai.turn_power_on()

                # -- receive radio messages --
                if len(radio.ai.receive_queue)>0:
                    message=radio.ai.receive_queue.pop()
                    
                    # avoid duplicates from other radio operators
                    if message not in self.owner.ai.squad.radio_receive_queue:
                        # ideally do some processing here 
                        self.owner.ai.squad.radio_receive_queue.append(message)

                # -- send radio messages --
                if len(self.owner.ai.squad.radio_send_queue)>0:
                    message=self.owner.ai.squad.radio_send_queue.pop()
                    vehicle.ai.radio.ai.send_message(message)
                    # maybe self.owner.ai.speak something here?

    #---------------------------------------------------------------------------
    def update_task_vehicle_crew(self):
        '''update task_vehicle_crew'''

        # this is for all crew
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        if vehicle.ai.vehicle_disabled:
            self.owner.ai.switch_task_exit_vehicle()
            return

        role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']

        if self.owner.is_player:
            self.update_task_vehicle_crew_player()
            return
        
        last_think_time=self.owner.ai.memory['task_vehicle_crew']['last_think_time']
        think_interval=self.owner.ai.memory['task_vehicle_crew']['think_interval']

        # --- think ----
        if self.owner.world.world_seconds-last_think_time>think_interval:
            # reset time
            self.owner.ai.memory['task_vehicle_crew']['last_think_time']=self.owner.world.world_seconds

            # universal check for empty priority spots
            if role.is_driver is False and role.is_gunner is False:
                # check if there are any empty roles
                for role in vehicle.ai.vehicle_crew:
                    if role.role_occupied is False:
                        if role.is_driver or role.is_gunner:
                            self.owner.ai.switch_task_vehicle_crew(vehicle,None)
                            return
                        
            # universal respond to vehicle being hit
            # this probably needs to be kept seperate from the role thinks as there is role overlap
            if len(self.owner.ai.memory['task_vehicle_crew']['vehicle_hits'])>0:
                self.think_vehicle_hit()
            
            # double check that we haven't decided to do something else like exit the vehicle
            if self.owner.ai.memory['current_task']!='task_vehicle_crew':
                return

            # note that roles can have multiple functions now
            if role.is_driver:
                # driver needs a fast refresh for smooth vehicle controls
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.2)
                self.think_vehicle_role_driver()
            if role.is_gunner:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.1,0.3)
                self.think_vehicle_role_gunner()
            if role.is_passenger:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.5,0.9)
                self.think_vehicle_role_passenger()
            if role.is_radio_operator:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.3,0.7)
                self.think_vehicle_role_radio_operator()
            if role.is_indirect_fire_gunner:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.3,0.7)
                self.think_vehicle_role_indirect_gunner()

            # the squad lead has some stuff to do independent of their vehicle role
            if self.owner==self.owner.ai.squad.squad_leader:
                # if we don't have a vehicle order, check to see if we can create 
                # one from tactical orders
                if self.owner.ai.memory['task_vehicle_crew']['vehicle_order'] is None:
                    self.owner.ai.squad_leader_review_orders()


        else:
            # some roles will want to do something every update cycle

            if role.is_gunner:
                if self.owner.ai.memory['task_vehicle_crew']['target'] is not None:
                    if self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle'] is not None:
                        self.action_vehicle_gunner_engage_target()
            if role.is_driver:
                self.action_vehicle_driver()

    #---------------------------------------------------------------------------
    def update_task_vehicle_crew_player(self):
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        role=self.owner.ai.memory['task_vehicle_crew']['vehicle_role']
        if role.is_gunner:
            # handle vehicle turret gun reloads for the player
            turret=role.turret
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading primary weapon':
                if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
                > turret.ai.primary_weapon_reload_speed):
                    self.owner.ai.reload_weapon(turret.ai.primary_weapon,vehicle,None)
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                else:
                    return
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='reloading coax gun':
                if (self.owner.world.world_seconds-self.owner.ai.memory['task_vehicle_crew']['reload_start_time'] 
                > turret.ai.coaxial_weapon_reload_speed):
                    self.owner.ai.reload_weapon(turret.ai.coaxial_weapon,vehicle,None)
                    self.owner.ai.memory['task_vehicle_crew']['current_action']='none'
                else:
                    return
            
            # this action is set by world. triggered by hitting 'w'
            if self.owner.ai.memory['task_vehicle_crew']['current_action']=='rotate turret':
                if self.rotate_turret(turret,self.owner.ai.memory['task_vehicle_crew']['calculated_turret_angle']):
                    # rotation achieved. we can remove this action
                    self.owner.ai.memory['task_vehicle_crew']['current_action']=''
