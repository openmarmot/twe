
'''
module : ai_vehicle.py
version : see module_version variable
Language : Python 3.x
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



#global variables

class AIVehicle(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # --- health stuff ----
        self.health=100

        # the ai group that this human is a part of 
        self.squad=None

        # array of engine objects
        self.engines=[]

        self.fuel_tanks=[]

        # open top aka passengers are viewable
        self.open_top=False
 

        # ----- controls ------

        # engine power. 0 is idle 1 is max
        # note - this needs to be propagated to the engines throttle_control variable
        self.throttle=0

        # brake_power 0 is none 1 is max
        self.brake_power=0

        self.brake_strength=100

        # planes that have wheel steering, cars, etc
        # 1 all the way left -1 all the way right. 0 neutral
        self.wheel_steering=0

        # ----- instruments ------


        # passengers  
        self.passengers=[]
        self.max_occupants=4 # max people that can be in the vehicle, including driver

        # set when a world_object claims the driver position. ai_human checks this to determine behavior
        self.driver=None

        # set when a world_object claims the gunner position. ai_human checks this to determine behavior
        self.gunner=None

        self.primary_weapon=None

        # 
        self.inventory=[]

        # the current speed
        self.current_speed=0.

        # max speed - this is in game terms and does not have a real world unit at the moment
        self.max_speed=0 


        # this is computed. should not be set by anything else
        self.acceleration=0


        # rate of climb in meters/second this is computed and can be positive or negative
        self.rate_of_climb=0

        # max rate of climb in meters/second. vehicle specific 
        self.max_rate_of_climb=0
        
        self.rotation_speed=0 # max rotation speed

        # update physics needs to know if its never been run before
        self.first_update=True


    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        if EVENT_DATA.is_projectile:
            self.health-=random.randint(3,15)
            engine.world_builder.spawn_object(self.owner.world,EVENT_DATA.world_coords,'dirt',True)

        elif EVENT_DATA.is_grenade:
            print('bonk')

    #---------------------------------------------------------------------------
    def event_add_inventory(self,EVENT_DATA):

        if EVENT_DATA.is_human:
            print('! Error - human added to vehicle inventory')
        else:
            self.inventory.append(EVENT_DATA) 


    #---------------------------------------------------------------------------
    def event_remove_inventory(self,EVENT_DATA):
        if EVENT_DATA in self.inventory:
            self.inventory.remove(EVENT_DATA)
            # make sure the obj world_coords reflect the obj that had it in inventory
            EVENT_DATA.world_coords=copy.copy(self.owner.world_coords)

    #---------------------------------------------------------------------------
    def handle_aileron_left(self):
        pass

    #---------------------------------------------------------------------------
    def handle_aileron_right(self):
        pass

    #---------------------------------------------------------------------------
    def handle_elevator_up(self):
        pass

    #---------------------------------------------------------------------------
    def handle_elevator_down(self):
        pass

    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if EVENT=='add_inventory':
            self.event_add_inventory(EVENT_DATA)
        elif EVENT=='collision':
            self.event_collision(EVENT_DATA)
        elif EVENT=='remove_inventory':
            self.event_remove_inventory(EVENT_DATA)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+EVENT)

    #---------------------------------------------------------------------------
    def handle_flaps_down(self):
        pass

    #---------------------------------------------------------------------------
    def handle_flaps_up(self):
        pass

    #---------------------------------------------------------------------------
    def handle_rudder_left(self):
        pass

    #---------------------------------------------------------------------------
    def handle_rudder_right(self):
        pass

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
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            print(self.owner.name+' has died')
            engine.world_builder.spawn_container('wreck',self.owner.world,self.owner.world_coords,self.owner.rotation_angle,self.owner.image_list[1],self.inventory)

            # human ai will figure out for itself that it needs to leave

            self.owner.world.remove_object(self.owner)

        # update engines
        for b in self.engines:
            b.throttle_control=self.throttle
            b.update()

        # update fuel tanks
        for b in self.fuel_tanks:
            b.update()

        self.update_fuel_system()

        if self.throttle>0:
            self.update_acceleration_calculation()
        else:
            self.acceleration=0

        self.update_physics()

        if self.primary_weapon!=None:
            # needs updates for time tracking and other stuff
            self.primary_weapon.update()

    
    #---------------------------------------------------------------------------
    def update_acceleration_calculation(self):
        self.acceleration=0

        # calculate total current engine force
        total_engine_force=0
        for b in self.engines:
            if b.ai.engine_on:
                total_engine_force+=b.ai.max_engine_force*b.ai.throttle_control

        self.acceleration=engine.math_2d.calculate_acceleration(
            total_engine_force,self.owner.rolling_resistance,
            self.owner.drag_coefficient,self.owner.world.air_density,
            self.owner.frontal_area,self.owner.weight)


    #---------------------------------------------------------------------------
    def update_fuel_system(self):

        for b in self.engines:
            if b.ai.fuel_consumed>0:
                fuel=0
                for c in self.fuel_tanks:
                    if fuel<b.ai.fuel_consumed:
                        c.ai.used_volume,fuel=engine.math_2d.get_transfer_results(c.ai.used_volume,fuel,b.ai.fuel_consumed)

                # give the fuel we got from the tanks to the engine
                # if the engine doesn't get enough fuel it will eventuall shut off
                b.ai.fuel_consumed-=fuel


    #---------------------------------------------------------------------------
    def update_physics(self):
        time_passed=self.owner.world.graphic_engine.time_passed_seconds

        heading_changed = False

        if self.first_update:
            self.first_update=False
            heading_changed=True

        # check control input

        # update rotation angle
        rotation_change=(self.rotation_speed*self.wheel_steering)*time_passed
        if rotation_change !=0 and self.current_speed>0:
            self.owner.rotation_angle+=rotation_change
            heading_changed=True
            

        # slowly zero out wheel steering. force to zero at low values to prevent dither
        if self.wheel_steering>0:
            self.wheel_steering-=1*time_passed
            if self.wheel_steering<0.05:
                self.wheel_steering=0
        elif self.wheel_steering<0:
            self.wheel_steering+=1*time_passed
            if self.wheel_steering>-0.05:
                self.wheel_steering=0

        # note this should be rethought. deceleration should happen at zero throttle with negative acceleration
        if self.throttle>0:

            if self.current_speed<self.max_speed:
                self.current_speed+=(self.acceleration*self.throttle)*time_passed

            self.throttle-=1*time_passed
            if self.throttle<0.05:
                self.throttle=0
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
            # normalize angles 
            if self.owner.rotation_angle>360:
                self.owner.rotation_angle=0
            elif self.owner.rotation_angle<0:
                self.owner.rotation_angle=360
            self.owner.heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
            self.owner.reset_image=True


        # move along vector
        self.owner.world_coords=engine.math_2d.moveAlongVector(self.current_speed,self.owner.world_coords,self.owner.heading,time_passed)

    






