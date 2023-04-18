
'''
module : ai_vehicle.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : a lot of this code came from ai_human but it has diverged a bit
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


        # current fuel type options : gas / diesel / none
        self.fuel_type='gas'
        # max fuel load in liters
        self.fuel_capacity=0
        # current fuel amount
        self.fuel=0

        # ----- controls ------

        # engine power. 0 is idle 1 is max
        self.throttle=0

        # brake_power 0 is none 1 is max
        self.brake_power=0

        # planes that have wheel steering, cars, etc
        # 1 all the way left -1 all the way right. 0 neutral
        self.wheel_steering=0

        # ----- instruments ------

        # distance between vehicle and ground
        self.altimeter=0

        # passengers  
        self.passengers=[]
        self.max_occupants=4 # max people that can be in the vehicle, including driver

        # set when a world_object claims the driver position. ai_human checks this to determine behavior
        self.driver=None

        # 
        self.inventory=[]

        # actual vehicle speed
        self.vehicle_speed=0.
        self.acceleration=0

        self.speed=0 # this is max speed at the moment
        self.rotation_speed=0 # max rotation speed

        # update physics needs to know if its never been run before
        self.first_update=True



    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # -- general stuff for all objects --
        if self.health<1:
            print(self.owner.name+' has died')
            engine.world_builder.spawn_container('wreck',self.owner.world,self.owner.world_coords,self.owner.rotation_angle,self.owner.image_list[1],self.inventory)

            # dump passengers
            for b in self.passengers:
                b.world_coords=[self.owner.world_coords[0]+float(random.randint(-15,15)),self.owner.world_coords[1]+float(random.randint(-15,15))]
                self.owner.world.add_object(b)
                self.driver=None

            self.owner.world.remove_object(self.owner)

        self.update_physics()

        if len(self.passengers)>0:

            for b in self.passengers:
                # update passenger coords. this fixes a lot of issues
                b.world_coords=copy.copy(self.owner.world_coords)
                b.update()
                # maybe run a normal ai.update here for each player


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
    def handle_steer_left(self):
        ''' recieve left steering input '''
        if self.altimeter<1:
            self.wheel_steering=1
    
    #---------------------------------------------------------------------------
    def handle_steer_right(self):
        ''' recieve left steering input '''
        if self.altimeter<1:
            self.wheel_steering=-1

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
        if rotation_change !=0 and self.vehicle_speed>0:
            self.owner.rotation_angle+=rotation_change
            heading_changed=True
            
        # left 
        #self.owner.rotation_angle+=self.owner.rotation_speed*time_passed
        # right
        #self.owner.rotation_angle-=self.owner.rotation_speed*time_passed

        # slowly zero out wheel steering. force to zero at low values to prevent dither
        if self.wheel_steering>0:
            self.wheel_steering-=1*time_passed
            if self.wheel_steering<0.05:
                self.wheel_steering=0
        elif self.wheel_steering<0:
            self.wheel_steering+=1*time_passed
            if self.wheel_steering>-0.05:
                self.wheel_steering=0


        if self.throttle>0 :
            if self.vehicle_speed<self.speed:
                self.vehicle_speed+=(self.acceleration*self.throttle)*time_passed
                if self.vehicle_speed<10:
                    self.vehicle_speed=10

            self.throttle-=1*time_passed
            if self.throttle<0.05:
                self.throttle=0

        if self.brake_power>0:
            self.vehicle_speed-=self.brake_power*self.acceleration*time_passed
            if self.vehicle_speed<5:
                self.vehicle_speed=0

        

        # deceleration 
        if self.vehicle_speed>5:
            self.vehicle_speed-=5*time_passed
        elif self.vehicle_speed<-5:
            self.vehicle_speed+=5*time_passed
        elif self.vehicle_speed<9 and self.vehicle_speed>-9:
            self.vehicle_speed=0

        # apply ground "rolling' friction  

        # apply air drag
        
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
        self.owner.world_coords=engine.math_2d.moveAlongVector(self.vehicle_speed,self.owner.world_coords,self.owner.heading,time_passed) 





