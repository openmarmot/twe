
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
from ai.ai_human_vehicle_gunner import AIHumanVehicleGunner
#import engine.global_exchange_rates

class AIHumanVehicle():
    def __init__(self, owner):
        self.owner=owner

        self.role_gunner=AIHumanVehicleGunner(self.owner)

        # distance tuning
        # when a vehicle is < this distance to a target it is considered arrived
        self.vehicle_arrival_distance=150

        

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
    def think_vehicle_role_commander(self):
        '''commander role'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

        # determine what the primary weapon is and primary gunner is
        primary_gunner=None
        for role in vehicle.ai.vehicle_crew:
            if role.is_gunner and role.role_occupied:
                if role.turret:
                    if role.turret.ai.primary_turret:
                        primary_gunner=role
                        break

        # for now we have no actions if we don't have a primary gunner
        if primary_gunner is None:
            return

        max_armor=0
        biggest_threat=None
        for v in self.owner.ai.vehicle_targets:
            if v.ai.vehicle_armor['front'][0]>max_armor:
                biggest_threat=v
        
        if biggest_threat:
            engage_primary,engage_primary_reason=self.owner.ai.calculate_engagement(primary_gunner.turret.ai.primary_weapon,biggest_threat)
            if engage_primary and primary_gunner.human.ai.memory['task_vehicle_crew']['target']!=biggest_threat :
                # tell the gunner to engage
                primary_gunner.human.ai.memory['task_vehicle_crew']['target']=biggest_threat
                self.owner.ai.speak(f'Gunner, prioritize the {biggest_threat.name} ')

            # check if we should re-orientate the vehicle to face the biggest threat


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
                    if current_action=='Waiting for driver to rotate the vehicle for fire mission':
                        if role.human.ai.memory['task_vehicle_crew']['fire_missions']:
                            fire_mission=role.human.ai.memory['task_vehicle_crew']['fire_missions'][0]
                            
                            # catch out of fuel 
                            current_fuel,max_fuel=vehicle.ai.read_fuel_gauge()
                            if current_fuel==0 and max_fuel>0:
                                engine.log.add_data('warn',f'ai_human_vehicle.think_vehicle_role_driver waiting for driver {self.owner.name}  to rotate {vehicle.name} and out of fuel, marking vehicle disabled',True)
                                vehicle.ai.vehicle_disabled=True
                                return

                            rotation_required=engine.math_2d.get_rotation(vehicle.world_coords,fire_mission.world_coords)
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
                    if current_action=='Waiting for driver to get in position for fire mission':
                        if role.human.ai.memory['task_vehicle_crew']['fire_missions']:
                            fire_mission=role.human.ai.memory['task_vehicle_crew']['fire_missions'][0]
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
                                # just so that we don't end up on top of the target
                                # note this doesn't really make sense. should get closer but not that close..
                                vehicle_order.world_coords=engine.math_2d.calculate_relative_position(fire_mission.world_coords,60,[200,200])
                                if vehicle.ai.is_transport:
                                    vehicle_order.exit_vehicle_when_finished=True
                                self.owner.ai.memory['task_vehicle_crew']['vehicle_order']=vehicle_order
                    # this is triggered by gunners that need to get closer to a tank to penetrate
                    if 'Waiting for driver to close distance' in current_action:
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
                                # just so that we don't end up on top of the target
                                vehicle_order.world_coords=engine.math_2d.calculate_relative_position(target.world_coords,60,[200,200])
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
                #engine.log.add_data('warn',f'ai_human_vehicle.think_vehicle_role_driver_drive_to_destination out of fuel. driver {self.owner.name} vehicle {vehicle.name} marking vehicle disabled',True)
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
    def think_vehicle_role_passenger(self):
        '''think.. as a passenger'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

        if self.owner.ai.human_targets or self.owner.ai.vehicle_targets:
            if vehicle.ai.current_speed<20:
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
            
        # gunner also uses this, do not want to over write 
        if vehicle_role.is_gunner is False:
            self.owner.ai.memory['task_vehicle_crew']['current_action']='Beep boop. operating the radio'
        
        self.owner.ai.radio_operator_ai.update()


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
                for available_role in vehicle.ai.vehicle_crew:
                    if available_role.role_occupied is False:
                        if available_role.is_driver or available_role.is_gunner:
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
                self.role_gunner.think()
            if role.is_passenger:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.3,3.5)
                self.think_vehicle_role_passenger()
            if role.is_radio_operator:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(0.3,0.7)
                self.think_vehicle_role_radio_operator()
            if role.is_commander:
                self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(1.1,2.5)
                self.think_vehicle_role_commander()

            # the squad lead has some stuff to do independent of their vehicle role
            if self.owner==self.owner.ai.squad.squad_leader:
                # if we don't have a vehicle order, check to see if we can create 
                # one from tactical orders
                if self.owner.ai.memory['task_vehicle_crew']['vehicle_order'] is None:
                    self.owner.ai.squad_leader_review_orders()


        else:
            # some roles will want to do something every update cycle

            if role.is_gunner:
                self.role_gunner.action()
                
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
