'''
repo : https://github.com/openmarmot/twe

notes : vehicle driver code
'''

#import built in modules
import random
import copy

#import custom packages
import engine.math_2d
import engine.log
from engine.vehicle_order import VehicleOrder

#import engine.global_exchange_rates

class AIHumanVehicleDriver():
    def __init__(self, owner):
        self.owner=owner

        # distance tuning
        # when a vehicle is < this distance to a target it is considered arrived
        self.vehicle_arrival_distance=150

    #---------------------------------------------------------------------------
    def action(self):
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

            if vehicle.ai.current_speed==0:
                # this throttle boost helps vehicle overcome bad terrain like trees 
                # otherwise a 0.2 isn't enough to move against a tree tile and they will get stuck not moving or rotating
                vehicle.ai.throttle = 0.5
                vehicle.ai.brake_power = 1
            elif vehicle.ai.current_speed > 10:
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
    def think_vehicle_order(self):
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
            self.think_drive_to_destination(order.world_coords,distance)
            return
        if order.order_tow_object:
            # future 
            return
        
   #---------------------------------------------------------------------------
    def think_drive_to_destination(self,destination,distance):
        '''perform actions necessary to start driving somewhere'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

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
                    engine.log.add_data('warn',f'ai_human_vehicle think_drive_to_destination max_fuel==0 for vehicle {vehicle.name}',True)

                # out of fuel.
                # disable the vehicle for now. in the future we will want to try and get fuel and refuel
                #engine.log.add_data('warn',f'ai_human_vehicle.think_drive_to_destination out of fuel. driver {self.owner.name} vehicle {vehicle.name} marking vehicle disabled',True)
                vehicle.ai.vehicle_disabled=True

    #---------------------------------------------------------------------------
    def check_rotation_required(self, rotation_required):
        '''handle common rotation logic'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        current_fuel,max_fuel=vehicle.ai.read_fuel_gauge()
        if current_fuel==0 and max_fuel>0:
            engine.log.add_data('warn',f'ai_human_vehicle.think_vehicle_role_driver waiting for driver {self.owner.name}  to rotate {vehicle.name} and out of fuel, marking vehicle disabled',True)
            vehicle.ai.vehicle_disabled=True
            return

        v=vehicle.rotation_angle
        if rotation_required>v-1 and rotation_required<v+1:
            self.owner.ai.memory['task_vehicle_crew']['current_action']='waiting'
            vehicle.ai.brake_power=1
            vehicle.ai.throttle=0
            self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(5,15)
            return
        #default
        self.owner.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']=rotation_required
        self.owner.ai.memory['task_vehicle_crew']['current_action']='rotating'
        return

    #---------------------------------------------------------------------------
    def create_vehicle_order_for_target(self, target_or_coords, offset_distance=60):
        '''create vehicle order to get close to target with fire mission'''
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
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
            vehicle_order.world_coords=engine.math_2d.calculate_relative_position(target_or_coords,offset_distance,[200,200])
            if vehicle.ai.is_transport:
                vehicle_order.exit_vehicle_when_finished=True
            self.owner.ai.memory['task_vehicle_crew']['vehicle_order']=vehicle_order

    #---------------------------------------------------------------------------
    def handle_gunner_busy_action(self, current_action, message):
        '''handle common waiting for gunner action'''
        self.owner.ai.memory['task_vehicle_crew']['current_action']=message
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle
        vehicle.ai.brake_power=1
        vehicle.ai.throttle=0
        self.owner.ai.memory['task_vehicle_crew']['think_interval']=random.uniform(5,10)
        return

    #---------------------------------------------------------------------------
    def think(self):
        vehicle=self.owner.ai.memory['task_vehicle_crew']['vehicle_role'].vehicle

        # precheck to make sure we aren't in combat 
        # first identify commander and primary gunner, then handle them with priority
        commander_role=None
        gunner_role=None
        
        for role in vehicle.ai.vehicle_crew:
            if role.role_occupied and role.is_commander:
                commander_role=role
                break
            if role.role_occupied and role.is_gunner:
                if role.turret and role.turret.ai and role.turret.ai.primary_weapon:
                    gunner_role=role
                    break

        # commander orders take priority - handle them first
        if commander_role:
            current_action=commander_role.human.ai.memory['task_vehicle_crew']['current_action']

            # this can be used for multiple things that require rotation
            if current_action=='Waiting for driver to rotate the vehicle':
                rotation_required=commander_role.human.ai.memory['task_vehicle_crew']['calculated_vehicle_angle']
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
        
        # only check gunner actions if commander doesn't need rotation
        if gunner_role:
            if gunner_role.turret.ai.primary_weapon:
                current_action=gunner_role.human.ai.memory['task_vehicle_crew']['current_action']
                
                # handle common busy states
                if 'reloading' in current_action:
                    return self.handle_gunner_busy_action(current_action,'waiting on crew to finish reloading')
                if 'Engaging' in current_action:
                    return self.handle_gunner_busy_action(current_action,'waiting on crew to finish engagement')
                if 'jam' in current_action:
                    return self.handle_gunner_busy_action(current_action,'waiting on gunner to finish clearing weapon jam')
                
                # handle rotation requests
                if current_action=='Waiting for driver to rotate the vehicle':
                    target=gunner_role.human.ai.memory['task_vehicle_crew']['target']
                    if target is not None:
                        rotation_required=engine.math_2d.get_rotation(vehicle.world_coords,target.world_coords)
                        return self.check_rotation_required(rotation_required)
                
                if current_action=='Waiting for driver to rotate the vehicle for fire mission':
                    if gunner_role.human.ai.memory['task_vehicle_crew']['fire_missions']:
                        fire_mission=gunner_role.human.ai.memory['task_vehicle_crew']['fire_missions'][0]
                        rotation_required=engine.math_2d.get_rotation(vehicle.world_coords,fire_mission.world_coords)
                        return self.check_rotation_required(rotation_required)
                
                if current_action=='Waiting for driver to get in position for fire mission':
                    if gunner_role.human.ai.memory['task_vehicle_crew']['fire_missions']:
                        fire_mission=gunner_role.human.ai.memory['task_vehicle_crew']['fire_missions'][0]
                        return self.create_vehicle_order_for_target(fire_mission.world_coords)
                
                # handle close distance requests
                if 'Waiting for driver to close distance' in current_action:
                    target=gunner_role.human.ai.memory['task_vehicle_crew']['target']
                    if target is not None:
                        return self.create_vehicle_order_for_target(target.world_coords)
        
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
            self.think_vehicle_order()
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

 