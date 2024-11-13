
'''
module : ai_vehicle.py
language : Python 3.x
email : andrew@openmarmot.com
notes : the vehicle isn't really meant to have AI. 
the only thing that should be here is physics and hardware stuff.
any AI would be handled by ai_human
'''

#import built in modules
import random
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder
import engine.penetration_calculator
import engine.log



#global variables

class AIVehicle(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # --- health stuff ----
        self.health=100

        # armor grade steel thickness in mm. standard soft aluminum/steel is a 0-1
        # this is the main vehicle
        self.vehicle_armor={}
        self.vehicle_armor['top']=0
        self.vehicle_armor['bottom']=0
        self.vehicle_armor['left']=0
        self.vehicle_armor['right']=0
        self.vehicle_armor['front']=0
        self.vehicle_armor['rear']=0


        # specific armor for the passenger compartment
        self.passenger_compartment_armor={}
        self.passenger_compartment_armor['top']=0
        self.passenger_compartment_armor['bottom']=0
        self.passenger_compartment_armor['left']=0
        self.passenger_compartment_armor['right']=0
        self.passenger_compartment_armor['front']=0
        self.passenger_compartment_armor['rear']=0


        # --- components ---

        # turrets - these are spawned and are in world 
        self.turrets=[]

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

        # passengers - note that passengers are not removed from the world, so they are still updated
        self.passengers=[]
        self.max_occupants=4 # max people that can be in the vehicle, including driver

        # set when a world_object claims the driver position. ai_human checks this to determine behavior
        self.driver=None


        # 
        self.inventory=[]


        # this is computed. should not be set by anything else
        self.acceleration=0


        # rate of climb in meters/second this is computed and can be positive or negative
        self.rate_of_climb=0

        # max rate of climb in meters/second. vehicle specific 
        self.max_rate_of_climb=3

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

    #---------------------------------------------------------------------------
    def handle_passenger_compartment_projectile_hit(self,projectile):
        distance=engine.math_2d.get_distance(self.owner.world_coords,projectile.ai.starting_coords,True)
        self.collision_log.append('Passenger compartment hit by '+projectile.name + ' at a distance of '+ str(distance))

        side=engine.math_2d.calculate_hit_side(self.owner.rotation_angle,projectile.rotation_angle)
        penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.passenger_compartment_armor[side])

        if penetration:
            self.health-=random.randint(1,3)
            if len(self.passengers)>0:
                passenger=random.choice(self.passengers)
                if 'task_vehicle_crew' in passenger.ai.memory:
                    if passenger.ai.memory['task_vehicle_crew']['role']=='passenger':
                        passenger.ai.handle_event('collision',projectile)
                        print(' ! Vehicle passenger hit ! ')
                else:
                    # this has happened. not sure why yet
                    engine.log.add_data('warn','ai_vehicle - passenger memory issue',True)
                    print(passenger.ai.memory)
            else:
                if random.randint(0,2)==2:
                    # extra shot at body damage
                    self.handle_vehicle_body_projectile_hit(projectile)
        else:
            # no penetration, but maybe we can have some other effect?
            pass


    #---------------------------------------------------------------------------
    def handle_vehicle_body_projectile_hit(self,projectile):
        distance=engine.math_2d.get_distance(self.owner.world_coords,projectile.ai.starting_coords,True)
        self.collision_log.append('Vehicle body hit by '+projectile.name + ' at a distance of '+ str(distance))

        side=engine.math_2d.calculate_hit_side(self.owner.rotation_angle,projectile.rotation_angle)
        penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.vehicle_armor[side])

        if penetration:
            if self.driver!=None:
                if random.randint(0,2)==2:
                    self.driver.ai.handle_event('collision',projectile)
            
            # should do component damage here
            self.health-=random.randint(1,25)

        else:
            # no penetration, but maybe we can have some other effect?
            pass
    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        

        if EVENT_DATA.is_projectile:
            
            # -- determine what area the projectile hit --
            area_hit='vehicle_body'
            
            if self.max_occupants>2:
                hit=random.randint(0,1)
                if hit==1:
                    area_hit='passenger_compartment'
            
            if len(self.turrets)>0:
                hit=random.randint(0,5)
                if hit==5:
                    area_hit='turret'

            if area_hit=='vehicle_body':
                self.handle_vehicle_body_projectile_hit(EVENT_DATA)
            elif area_hit=='passenger_compartment':
                self.handle_passenger_compartment_projectile_hit(EVENT_DATA)
            elif area_hit=='turret':
                # pass it on for the turret to handle
                turret=random.choice(self.turrets)
                turret.ai.handle_event('collision',EVENT_DATA)
            else:
                engine.log.add_data('Error','ai_vehicle.calculate_projectile_damage - unknown area hit: '+area_hit,True)

            engine.world_builder.spawn_object(self.owner.world,EVENT_DATA.world_coords,'dirt',True)
            engine.world_builder.spawn_sparks(self.owner.world,self.owner.world_coords,random.randint(1,2))

        elif EVENT_DATA.is_grenade:
            print('bonk')
        else:
            engine.log.add_data('error','ai_vehicle event_collision - unhandled collision type'+EVENT_DATA.name,True)

    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):

        if EVENT_DATA.is_human:
            # we don't want humans in here
            print('! Error - human added to vehicle inventory')
        else:

            if EVENT_DATA.is_radio:
                if self.radio==None:
                    self.radio=EVENT_DATA

            # put whatever it is in the inventory
            self.inventory.append(EVENT_DATA) 


    #---------------------------------------------------------------------------
    def event_remove_inventory(self,EVENT_DATA):
        if EVENT_DATA in self.inventory:
            self.inventory.remove(EVENT_DATA)

            if EVENT_DATA.is_radio:
                if self.radio==EVENT_DATA:
                    self.radio=None

            # make sure the obj world_coords reflect the obj that had it in inventory
            EVENT_DATA.world_coords=copy.copy(self.owner.world_coords)

    #---------------------------------------------------------------------------
    def handle_aileron_left(self):
        self.ailerons=1

    #---------------------------------------------------------------------------
    def handle_aileron_right(self):
        self.ailerons=-1

    #---------------------------------------------------------------------------
    def handle_death(self):
        engine.world_builder.spawn_container('wreck',self.owner,1)
        
        dm=''
        dm+=(self.owner.name+' died.')
        dm+=('\n  -- collision log --')
        for b in self.collision_log:
            dm+=('\n --'+b)
        dm+=('\n  -------------------')
        

        print(dm)

        # human ai will figure out for itself that it needs to leave
        # remove from world
        self.owner.world.remove_queue.append(self.owner)

    #---------------------------------------------------------------------------
    def handle_elevator_up(self):
        self.elevator=-1

    #---------------------------------------------------------------------------
    def handle_elevator_down(self):
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
        self.flaps=1

    #---------------------------------------------------------------------------
    def handle_flaps_up(self):
        self.flaps=0

    #---------------------------------------------------------------------------
    def handle_rudder_left(self):
        self.rudder=-1

    #---------------------------------------------------------------------------
    def handle_rudder_right(self):
        self.rudder=1

    #---------------------------------------------------------------------------
    def handle_start_engines(self):
        for b in self.engines:
            if b.ai.engine_on==False:
                b.ai.engine_on=True
                if b.ai.internal_combustion:
                    #smoke!
                    heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle+180)
                    smoke_coords=engine.math_2d.calculate_relative_position(self.owner.world_coords,self.owner.rotation_angle,b.ai.exhaust_position_offset)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,smoke_coords,heading)

    #---------------------------------------------------------------------------
    def handle_stop_engines(self):
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

        # -- general stuff for all objects --
        if self.health<1:
            self.handle_death()

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

    
    #---------------------------------------------------------------------------
    def update_acceleration_calculation(self):
        self.acceleration=0

        # calculate total current engine force
        total_engine_force=0
        for b in self.engines:
            if b.ai.engine_on:
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

        # update passenger rotation and position
        for b in self.passengers:
            # coordinates + altitude
            b.world_coords=copy.copy(self.owner.world_coords)
            b.altitude=self.owner.altitude

            # rotate to match vehicle heading
            if self.open_top:
                if b.rotation_angle!=self.owner.rotation_angle:
                    b.rotation_angle=self.owner.rotation_angle
                    b.reset_image=True
        
    #---------------------------------------------------------------------------
    def update_electrical_system(self):

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

        
        # apply ground "rolling' friction  

        # apply air drag

        # adjust altitude
        self.owner.altitude+=self.rate_of_climb*time_passed
        
        #  reset image if heading has changed 
        if heading_changed:
            self.update_heading()


        # move along vector
        if self.current_speed>0:
            self.owner.world_coords=engine.math_2d.moveAlongVector(self.current_speed,self.owner.world_coords,self.owner.heading,time_passed)
            
        # update the relative position and rotation of child objects
        if self.current_speed>0 or heading_changed:
            self.update_child_position_rotation()
    #---------------------------------------------------------------------------
    def update_rate_of_climb_calculation(self):

        # need some sort of actual algo here
        lift=9.8 # counter act gravity for now
        if self.current_speed>self.stall_speed:
            # if elevator is zero then rate of climb will be zero
            # if elevator is up (-1) then rate of climb will be negative
            self.rate_of_climb=(self.max_rate_of_climb*self.throttle*self.elevator)+lift





