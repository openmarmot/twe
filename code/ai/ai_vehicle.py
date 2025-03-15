
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : the vehicle isn't really meant to have AI. 
the only thing that should be here is physics and hardware stuff.
any AI would be handled by ai_human
'''

#import built in modules
import random
import copy

#import custom packages
import engine.math_2d
import engine.world_builder
import engine.penetration_calculator
import engine.log
from engine.hit_data import HitData



#global variables

class AIVehicle():
    def __init__(self, owner):
        self.owner=owner

        # --- armor ---
        #[side][armor thickness,armor slope,spaced_armor_thickness]
        # slope 0 degrees is vertical, 90 degrees is horizontal
        # armor grade steel thickness in mm. standard soft aluminum/steel is a 0-1
        # this is the main vehicle
        self.vehicle_armor={}
        self.vehicle_armor['top']=[0,0,0]
        self.vehicle_armor['bottom']=[0,0,0]
        self.vehicle_armor['left']=[0,0,0]
        self.vehicle_armor['right']=[0,0,0]
        self.vehicle_armor['front']=[0,0,0]
        self.vehicle_armor['rear']=[0,0,0]

        # specific armor for the passenger compartment
        self.passenger_compartment_armor={}
        self.passenger_compartment_armor['top']=[0,0,0]
        self.passenger_compartment_armor['bottom']=[0,0,0]
        self.passenger_compartment_armor['left']=[0,0,0]
        self.passenger_compartment_armor['right']=[0,0,0]
        self.passenger_compartment_armor['front']=[0,0,0]
        self.passenger_compartment_armor['rear']=[0,0,0]

        # results in a chance for high damage from a passenger compartment hit
        # this is meant to be large caliber ammo - like tank shells
        self.passenger_compartment_ammo_racks=False

        # ---

        # gears
        self.transmission={}
        self.current_gear='drive'
        self.transmission['drive']=[1]
        self.transmission['neutral']=[0]
        self.transmission['reverse']=[-1]

        # --- components ---

        # turrets - these are spawned and are in world 
        # !! Note these should be added in order of importance due to know the driver handles requests
        self.turrets=[]

        # for rotary wing .. vehicles
        self.rotors=[]

        # array of engine objects
        self.engines=[]

        # array of fuel tank objects
        self.fuel_tanks=[]

        # array of battery objects
        self.batteries=[]

        # radio - only one for now
        self.radio=None

        # amp output for the alternator(s)
        # if i lose more of my sanity it would be nice to model individual alternators
        self.alternator_amps=15
        
        # open top aka passengers are viewable
        self.open_top=False

        # only stores main gun ammo
        self.ammo_rack=[]
        self.ammo_rack_capacity=0 # max capacity

        # wheels 
        self.max_wheels=0 # maximum wheels that can be fitted to the vehicle
        self.min_weels=0 # minimum number of healthy wheels to move
        self.wheels=[]
        self.spare_wheels=[]
        self.max_spare_wheels=0

        # ----- controls ------

        # engine power. 0 is idle 1 is max
        # note - this needs to be propagated to the engines throttle_control variable
        self.throttle=0

        # if true throttle returns to zero slowly
        # should generally be true for cars and false for planes
        self.throttle_zero=True

        # if true brake returns to zero quickly
        # should be true for everything (?)
        self.brake_zero=True

        # brake_power 0 is none 1 is max
        self.brake_power=0

        self.brake_strength=100

        # planes that have wheel steering, cars, etc
        # 1 all the way left -1 all the way right. 0 neutral
        self.wheel_steering=0


        # - airplane controls -

        # generally negative is left or down. zero is neutral
        # except for flaps. flaps up is zero

        self.ailerons=0
        self.elevator=0
        self.flaps=0
        self.rudder=0

        # -- crew --
 

        # {'role',[occupied bool,human_object game_obj,seat_rotation angle float,seat_offset [0,0],visible bool],role_related_object}
        self.vehicle_crew={}

        # --
        # this gives the AI clues as to how they should use the vehicle
        self.vehicle_role=''
        # whether the crew needs is_afv_trained
        self.requires_afv_training=False

        #
        self.towed_object=None
        self.tow_offset=[150,0]
        self.in_tow=False # whether this vehicle is being towed currently


        # 
        self.inventory=[]


        # this is computed. should not be set by anything else
        self.acceleration=0


        # rate of climb in meters/second this is computed and can be positive or negative
        self.rate_of_climb=0

        # max rate of climb in meters/second. vehicle specific 
        self.max_rate_of_climb=0

        # the current speed
        self.current_speed=0.

        # max speed - this is in game units
        self.max_speed=0 

        # max offroad speed 
        self.max_offroad_speed=0

        # whether we are offroad or not
        self.offroad=True

        # minimum speed needed to take off

        # stall speed. should be affected by angle of attack
        self.stall_speed=0
        
        self.rotation_speed=0 # max rotation speed around axis (wheel steering)

        # update physics needs to know if its never been run before
        self.first_update=True

        # used for death message 
        self.collision_log=[]

        # used for targeting
        self.recent_noise_or_move=False
        # reset in update
        self.last_noise_or_move_time=0 # in world.world_seconds
        self.recent_noise_or_move_reset_seconds=30

        # vehicle is damaged to the point that it is out of action
        # note this is just a clue for the AI and does not do anything
        self.vehicle_disabled=False

    #---------------------------------------------------------------------------
    def add_hit_data(self,projectile,penetration,side,distance,compartment_hit):
        '''add hit data to the collision log'''
        hit=HitData(self.owner,projectile,penetration,side,distance,compartment_hit)
        self.collision_log.append(hit)
        if self.owner.world.hit_markers:
            marker=engine.world_builder.spawn_object(self.owner.world,self.owner.world_coords,'hit_marker',True)
            marker.ai.setup(self.owner,hit)
    #---------------------------------------------------------------------------
    def attach_tow_object(self,tow_object):
        '''attach an object for towing'''

        if self.towed_object is not None:
            self.detach_tow_object()
        
        self.towed_object=tow_object
        if self.towed_object.is_vehicle:
            self.towed_object.ai.in_tow=True

    #---------------------------------------------------------------------------
    def check_if_human_in_vehicle(self,human):
        '''returns a bool as to whether the human is in the vehicle'''
        for value in self.vehicle_crew.values():
            if value[0] is True:
                if value[1]==human:
                    return True
        return False

    #---------------------------------------------------------------------------
    def check_if_vehicle_is_full(self):
        '''returns a bool as to whether the vehicle is full'''

        # note - need to think how gunners fit into this

        for value in self.vehicle_crew.values():
            if value[0] is False:
                return False
            
        return True
    
    #---------------------------------------------------------------------------
    def check_if_vehicle_is_crewed(self):
        '''returns a bool as to whether there is live crew in the vehicle'''
        for value in self.vehicle_crew.values():
            if value[0] is True:
                if value[1].ai.health>0:
                    return True
        return False

    #---------------------------------------------------------------------------
    def detach_tow_object(self):
        '''detach an object that we are towing'''
        if self.towed_object!=None:
            if self.towed_object.is_vehicle:
                self.towed_object.ai.in_tow=False
            self.towed_object=None

    #---------------------------------------------------------------------------
    def event_collision(self,event_data):
        '''handle a collision event'''

        if event_data.is_projectile:
            # avoids hits on dead vehicles that haven't been removed from the game yet
            
            # -- determine what area the projectile hit --
            area_hit='vehicle_body'
            

            hit=random.randint(0,1)
            if hit==1:
                area_hit='passenger_compartment'
            
            if len(self.turrets)>0:
                hit=random.randint(0,4)
                if hit==5:
                    area_hit='turret'

            if area_hit=='vehicle_body':
                self.handle_vehicle_body_projectile_hit(event_data)
            elif area_hit=='passenger_compartment':
                self.handle_passenger_compartment_projectile_hit(event_data)
            elif area_hit=='turret':
                # pass it on for the turret to handle
                turret=random.choice(self.turrets)
                turret.ai.handle_event('collision',event_data)
            else:
                engine.log.add_data('Error','ai_vehicle.calculate_projectile_damage - unknown area hit: '+area_hit,True)

            #engine.world_builder.spawn_object(self.owner.world,event_data.world_coords,'dirt',True)
            engine.world_builder.spawn_sparks(self.owner.world,event_data.world_coords,random.randint(1,2))


        elif event_data.is_grenade:
            print('bonk')
        else:
            engine.log.add_data('error','ai_vehicle event_collision - unhandled collision type'+event_data.name,True)

    #---------------------------------------------------------------------------
    def event_add_inventory(self,event_data):
        '''add an object to the inventory'''

        if event_data.is_human:
            # we don't want humans in here
            print('! Error - human added to vehicle inventory')
        else:

            if event_data.is_radio:
                if self.radio==None:
                    self.radio=event_data

            # put whatever it is in the inventory
            self.inventory.append(event_data) 

    #---------------------------------------------------------------------------
    def event_remove_inventory(self,event_data):
        '''remove an object from the inventory'''
        if event_data in self.inventory:
            self.inventory.remove(event_data)

            if event_data.is_radio:
                if self.radio==event_data:
                    self.radio=None

            # make sure the obj world_coords reflect the obj that had it in inventory
            event_data.world_coords=copy.copy(self.owner.world_coords)

    #---------------------------------------------------------------------------
    def handle_component_damage(self,damaged_component,projectile):
        '''handle damage to a component'''
        if damaged_component=='driver':
            if self.vehicle_crew['driver_projectile'][0] is True:
                self.vehicle_crew['driver'][1].ai.handle_event('collision',projectile)
        elif damaged_component=='engine':
            for b in self.engines:
                b.ai.damaged=True
                if b.ai.internal_combustion:
                    #smoke!
                    heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle+180)
                    smoke_coords=engine.math_2d.calculate_relative_position(self.owner.world_coords,
                                            self.owner.rotation_angle,b.ai.exhaust_position_offset)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,smoke_coords,heading)
            self.vehicle_disabled=True
        elif damaged_component=='all_crew':
            for key,value in self.vehicle_crew.items():
                if value[0] is True:
                    value[1].ai.handle_event('collision',projectile)
        elif damaged_component=='random_crew_projectile':
            for key,value in self.vehicle_crew.items():
                if value[0] is True:
                    if random.randint(0,1)==1:
                        value[1].ai.handle_event('collision',projectile)
        elif damaged_component=='random_crew_explosion':
            for key,value in self.vehicle_crew.items():
                if value[0] is True:
                    if random.randint(0,1)==1:
                        value[1].ai.handle_event('explosion',random.randint(30,150))
        elif damaged_component=='random_crew_fire':
            for key,value in self.vehicle_crew.items():
                if value[0] is True:
                    if random.randint(0,1)==1:
                        value[1].ai.handle_hit_with_flame()
        elif damaged_component=='ammo_rack':
            temp=random.randint(0,self.ammo_rack_capacity)
            if temp<len(self.ammo_rack):
                self.handle_component_damage('random_crew_explosion',None)
                self.handle_component_damage('engine',None)
                self.vehicle_disabled=True
                for b in self.turrets:
                    b.turret_jammed=True
                    if b.ai.primary_weapon:
                        b.ai.primary_weapon.ai.damaged=True
                    if b.ai.coaxial_weapon:
                        b.ai.coaxial_weapon.ai.damaged=True
                engine.world_builder.spawn_explosion_and_fire(self.owner.world,self.owner.world_coords,10,30)


    #---------------------------------------------------------------------------
    def handle_passenger_compartment_projectile_hit(self,projectile):
        '''handle a projectile hit to the passenger compartment'''
        distance=engine.math_2d.get_distance(self.owner.world_coords,projectile.ai.starting_coords)

        side=engine.math_2d.calculate_hit_side(self.owner.rotation_angle,projectile.rotation_angle)
        penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.passenger_compartment_armor[side])
        self.add_hit_data(projectile,penetration,side,distance,'Passenger Compartment')
        if penetration:
            damaged_component=random.choice(['random_crew_projectile','ammo_rack','miraculously unharmed'])
            self.handle_component_damage(damaged_component,projectile)

        else:
            # no penetration, but maybe we can have some other effect?
            pass

    #---------------------------------------------------------------------------
    def handle_vehicle_body_projectile_hit(self,projectile):
        '''handle a projectile hit to the vehicle body'''
        distance=engine.math_2d.get_distance(self.owner.world_coords,projectile.ai.starting_coords)

        side=engine.math_2d.calculate_hit_side(self.owner.rotation_angle,projectile.rotation_angle)
        penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.vehicle_armor[side])
        self.add_hit_data(projectile,penetration,side,distance,'Vehicle Body')
        if penetration:
            damaged_component=random.choice(['driver_projectile','engine','miraculously unharmed'])
            self.handle_component_damage(damaged_component,projectile)

        else:
            # no penetration, but maybe we can have some other effect?
            pass

    #---------------------------------------------------------------------------
    def handle_aileron_left(self):
        '''handle left aileron input'''
        self.ailerons=1

    #---------------------------------------------------------------------------
    def handle_aileron_right(self):
        '''handle right aileron input'''
        self.ailerons=-1

    #---------------------------------------------------------------------------
    def handle_elevator_up(self):
        '''handle elevator up event'''
        self.elevator=-1

    #---------------------------------------------------------------------------
    def handle_elevator_down(self):
        '''handle elevator down event'''
        self.elevator=1

    #---------------------------------------------------------------------------
    def handle_event(self, event, event_data):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # event_data - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if event=='add_inventory':
            self.event_add_inventory(event_data)
        elif event=='collision':
            self.event_collision(event_data)
        elif event=='remove_inventory':
            self.event_remove_inventory(event_data)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+event)

    #---------------------------------------------------------------------------
    def handle_flaps_down(self):
        '''handle flaps down event'''
        self.flaps=1

    #---------------------------------------------------------------------------
    def handle_flaps_up(self):
        '''handle flaps up event'''
        self.flaps=0

    #---------------------------------------------------------------------------
    def handle_hit_with_flame(self):
        '''handle the vehicle being hit with flame'''

        if self.open_top:
            self.handle_component_damage('random_crew_fire',None)
        else:
            if random.randint(0,3)==3:
                self.handle_component_damage('random_crew_fire',None)

    #---------------------------------------------------------------------------
    def handle_rudder_left(self):
        '''handle left rudder input'''
        self.rudder=-1

    #---------------------------------------------------------------------------
    def handle_rudder_right(self):
        '''handle right rudder input'''
        self.rudder=1

    #---------------------------------------------------------------------------
    def handle_start_engines(self):
        '''handle starting the engines'''
        for b in self.engines:
            if b.ai.engine_on==False:
                if b.ai.damaged is False:
                    b.ai.engine_on=True
                # smoke no matter what
                if b.ai.internal_combustion:
                    #smoke!
                    heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle+180)
                    smoke_coords=engine.math_2d.calculate_relative_position(self.owner.world_coords,
                                            self.owner.rotation_angle,b.ai.exhaust_position_offset)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,smoke_coords,heading)

    #---------------------------------------------------------------------------
    def handle_stop_engines(self):
        '''handle stopping the engines'''
        for b in self.engines:
            if b.ai.engine_on==True:
                b.ai.engine_on=False

    #---------------------------------------------------------------------------
    def handle_steer_left(self):
        ''' recieve left steering input '''
        if self.owner.altitude<1:
            self.wheel_steering=1
    
    #---------------------------------------------------------------------------
    def handle_steer_right(self):
        ''' recieve left steering input '''
        if self.owner.altitude<1:
            self.wheel_steering=-1

    #---------------------------------------------------------------------------
    def handle_steer_neutral(self):
        '''reset steerign to zero'''
        self.wheel_steering=0

    #---------------------------------------------------------------------------
    def handle_throttle_up(self):
        '''adjust the throttle a bit over time'''
        self.throttle+=1*self.owner.world.time_passed_seconds
        if self.throttle>1:
            self.throttle=1

        if self.throttle_zero:
            print('Warning - throttle_zero interferes with throttle up')

    #---------------------------------------------------------------------------
    def handle_throttle_down(self):
        '''adjust the throttle a bit over time'''
        self.throttle-=1*self.owner.world.time_passed_seconds
        if self.throttle<0:
            self.throttle=0

        if self.throttle_zero:
            print('Warning - throttle_zero interferes with throttle up')

    #---------------------------------------------------------------------------
    def neutral_controls(self):
        ''' return controls to neutral over time'''

        # controls should return to neutral over time 
        time_passed=self.owner.world.time_passed_seconds

        #return wheel to neutral
        self.wheel_steering=engine.math_2d.regress_to_zero(self.wheel_steering,time_passed)

        
        # is this wanted??
        # return throttle to neutral
        if self.throttle_zero:
            self.throttle=engine.math_2d.regress_to_zero(self.throttle,time_passed)

        if self.brake_zero:
            self.brake_power=engine.math_2d.regress_to_zero(self.brake_power,time_passed)

         # aierlons 
        self.ailerons=engine.math_2d.regress_to_zero(self.ailerons,time_passed)

        # elevator
        self.elevator=engine.math_2d.regress_to_zero(self.elevator,time_passed)

        # rudder       
        self.rudder=engine.math_2d.regress_to_zero(self.rudder,time_passed)


    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # update engines
        for b in self.engines:
            b.throttle_control=self.throttle
            b.update()

        # updates fuel tanks and handles fuel flow to engines
        self.update_fuel_system()

        # update batteries and electrical distribution
        self.update_electrical_system()

        # update radio
        if self.radio!=None:
            self.radio.world_coords=copy.copy(self.owner.world_coords)
            self.radio.update()

        if self.throttle>0:
            self.update_acceleration_calculation()
        else:
            self.acceleration=0

        # update rate of climb
        self.update_rate_of_climb_calculation()

        self.update_physics()

        # bring controls back to neutral slowly over time
        self.neutral_controls()
        
        if self.recent_noise_or_move:
            if self.owner.world.world_seconds-self.last_noise_or_move_time>self.recent_noise_or_move_reset_seconds:
                self.recent_noise_or_move=False

    #---------------------------------------------------------------------------
    def update_acceleration_calculation(self):
        '''update the acceleration calculation'''
        self.acceleration=0

        # calculate total current engine force
        total_engine_force=0
        for b in self.engines:
            if b.ai.engine_on and b.ai.damaged is False:
                total_engine_force+=b.ai.max_engine_force*b.ai.throttle_control

        # prevents this from going negative. but maybe we want that?
        # 0 engine force could result in negative accelleration 
        if total_engine_force>0:
            self.acceleration=engine.math_2d.calculate_acceleration(
                total_engine_force,self.owner.rolling_resistance,
                self.owner.drag_coefficient,self.owner.world.air_density,
                self.owner.frontal_area,self.owner.weight)
            
    #---------------------------------------------------------------------------
    def update_child_position_rotation(self):
        '''update the position and rotation of child objects'''
        # this is only called when the vehicle position or rotation changes
        # it is also called by human_ai when it enters the vehicle

        # update passenger rotation and position
        for key,value in self.vehicle_crew.items():
            # if position is occupied
            if value[0]==True:

                # stuff to change no matter what
                value[1].altitude=self.owner.altitude
                # if position is visible
                if value[4]==True:
                    # set the world coords with the offset
                    value[1].world_coords=engine.math_2d.calculate_relative_position(self.owner.world_coords,self.owner.rotation_angle,value[3])
                    value[1].rotation_angle=self.owner.rotation_angle+value[2]
                    value[1].reset_image=True
                else:
                    # just a simple position
                    value[1].world_coords=copy.copy(self.owner.world_coords)



        # update towed object
        if self.towed_object!=None:
            self.towed_object.world_coords=engine.math_2d.calculate_relative_position(self.owner.world_coords,self.owner.rotation_angle,self.tow_offset)
            if self.towed_object.rotation_angle!=self.owner.rotation_angle:
                self.towed_object.rotation_angle=self.owner.rotation_angle
                self.towed_object.reset_image=True

            if self.towed_object.is_vehicle:
                # need to specifically call this as it will not trigger on the towed object itself as its engine is not used
                self.towed_object.ai.update_child_position_rotation()
        
    #---------------------------------------------------------------------------
    def update_electrical_system(self):
        '''update the electrical system'''
        # update batteries
        for b in self.batteries:
            b.update()
        
        #electrical units are in hours for whatever reason. gotta get the conversion
        time_passed_hours=self.owner.world.time_passed_seconds/3600

        charge=self.alternator_amps*time_passed_hours # I think the result of this is amp hours ?
        
        # charge batteries with the alternator 
        # theoretically the charge should be divided up amongst all the batteries?
        # but then we should be modelling multiple alternators 
        for b in self.batteries:
            b.ai.recharge(charge)

    #---------------------------------------------------------------------------
    def update_fuel_system(self):
        ''' distributes fuel from the tanks to the engines'''

        # update fuel tanks
        for b in self.fuel_tanks:
            b.update()

        # well this is not great

        for b in self.engines:
            if b.ai.fuel_consumed>0:
                fuel=0
                for c in self.fuel_tanks:
                    if fuel<b.ai.fuel_consumed:
                        if len(c.ai.inventory)==1: # fuel tank should have one object - the fuel liquid
                            if c.ai.inventory[0].is_liquid:
                                if c.ai.inventory[0].name in b.ai.fuel_type:
                                    c.ai.inventory[0].volume,fuel=engine.math_2d.get_transfer_results(c.ai.inventory[0].volume,fuel,b.ai.fuel_consumed)
                                else:
                                    print('warn - fuel type mismatch')
                                    # note - this should hard kill the engine
                            else:
                                print('Error: object in fuel tank is not liquid')
                        else:
                            pass 
                            # should deal with contamination - but could also be empty

                # give the fuel we got from the tanks to the engine
                # if the engine doesn't get enough fuel it will eventuall shut off
                b.ai.fuel_consumed-=fuel


    #---------------------------------------------------------------------------
    def update_heading(self):
        '''normalize rotation and update heading'''
        # mostly called by update_physics when rotation changes, but also
        # needed when the the rotation angle of the vehicle has to be fixed externally
        self.owner.rotation_angle=engine.math_2d.get_normalized_angle(self.owner.rotation_angle)
        self.owner.heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
        self.owner.reset_image=True

    #---------------------------------------------------------------------------
    def update_physics(self):
        '''update the physics of the vehicle'''
        time_passed=self.owner.world.time_passed_seconds

        heading_changed = False

        if self.first_update:
            self.first_update=False
            heading_changed=True

        # check control input

        # update rotation angle on the ground
        if self.owner.altitude<1:
            rotation_change=(self.rotation_speed*self.wheel_steering)*time_passed
        # update rotation angle in the air
        else:
            rotation_change=(self.rotation_speed*self.ailerons)*time_passed

        if rotation_change !=0 and self.current_speed>0:
            self.owner.rotation_angle+=rotation_change
            heading_changed=True
                   
        # note this should be rethought. deceleration should happen at zero throttle with negative acceleration
        if self.throttle>0:
            if self.offroad:
                if self.current_speed<self.max_offroad_speed:
                    self.current_speed+=(self.acceleration*self.throttle)*time_passed
            else:
                if self.current_speed<self.max_speed:
                    self.current_speed+=(self.acceleration*self.throttle)*time_passed
        else:
            # just in case the throttle went negative
            self.throttle=0
            
            # deceleration 
            # this may need tuning 
            if self.current_speed>5:
                self.current_speed-=5*time_passed
            elif self.current_speed<-5:
                self.current_speed+=5*time_passed
            elif self.current_speed<9 and self.current_speed>-9:
                self.current_speed=0

            if self.brake_power>0:
                self.current_speed-=self.brake_power*self.brake_strength*time_passed
                if self.current_speed<5:
                    self.current_speed=0

        # apply air drag

        # adjust altitude
        self.owner.altitude+=self.rate_of_climb*time_passed
        
        #  reset image if heading has changed 
        if heading_changed:
            self.update_heading()


        # move along vector
        if self.current_speed>0:

            self.recent_noise_or_move=True
            self.last_noise_or_move_time=self.owner.world.world_seconds

            # apply gearbox
            gear_velocity=self.current_speed*self.transmission[self.current_gear][0]

            self.owner.world_coords=engine.math_2d.moveAlongVector(gear_velocity,self.owner.world_coords,self.owner.heading,time_passed)
            
        # update the relative position and rotation of child objects
        if self.current_speed>0 or heading_changed:
            self.update_child_position_rotation()
    #---------------------------------------------------------------------------
    def update_rate_of_climb_calculation(self):
        '''update the rate of climb calculation'''
        if self.max_rate_of_climb!=0:
            # need some sort of actual algo here
            lift=9.8 # counter act gravity for now
            if self.current_speed>self.stall_speed:
                # if elevator is zero then rate of climb will be zero
                # if elevator is up (-1) then rate of climb will be negative
                self.rate_of_climb=(self.max_rate_of_climb*self.throttle*self.elevator)+lift





