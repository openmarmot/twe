
'''
repo : https://github.com/openmarmot/twe

notes : helicopter rotors and ... hopefully something else? 
'''

#import built in modules
import copy

#import custom packages
import engine.math_2d
import engine.log
import engine.penetration_calculator
import random


#global variables

class AIRotor():
    def __init__(self, owner):
        self.owner=owner

        #[side][armor thickness,armor slope,spaced_armor_thickness]
        # slope 0 degrees is vertical, 90 degrees is horizontal
        # armor grade steel thickness in mm. standard soft aluminum/steel is a 0-1

        self.health=100

        # offset to position it correctly on a vehicle. vehicle specific 
        self.position_offset=[0,0]

        # this is relative to the vehicle
        # really + or - a certain amount of degrees
        self.rotor_rotation=0

        # gunner requested rotation change
        self.rotation_change=0

        # rotation range for the turret
        self.rotation_range=[-20,20]

        # speed of rotation
        self.current_rotation_speed=0
        self.rotation_rate_of_change=8
        self.max_rotation_speed=450

        self.vehicle=None
        self.last_vehicle_position=[0,0]
        self.last_vehicle_rotation=0

        self.engine=None # the engine driving the rotor


        self.collision_log=[]

    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        
        self.health-=random.randint(1,100)

    #---------------------------------------------------------------------------
    def handle_event(self, event, event_data):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # event_data - most likely a world_object but could be anything


        if event=='collision':
            self.event_collision(event_data)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+event)

    #---------------------------------------------------------------------------
    def handle_rotate_left(self):
        self.rotation_change=1

    #---------------------------------------------------------------------------
    def handle_rotate_right(self):
        self.rotation_change=-1



    #---------------------------------------------------------------------------
    def neutral_controls(self):
        ''' return controls to neutral over time'''


        if self.rotation_change!=0:
            # controls should return to neutral over time 
            time_passed=self.owner.world.time_passed_seconds

            #return wheel to neutral
            self.rotation_change=engine.math_2d.regress_to_zero(self.rotation_change,time_passed)

    #---------------------------------------------------------------------------
    def update(self):

        
        self.update_physics()

        #self.neutral_controls()

    #---------------------------------------------------------------------------
    def update_physics(self):
        time_passed=self.owner.world.time_passed_seconds
        moved=False

        if self.engine.ai.engine_on:
            self.rotation_change=-1
            if self.current_rotation_speed<self.max_rotation_speed:
                self.current_rotation_speed+=self.rotation_rate_of_change*time_passed
        else:
            if self.current_rotation_speed>0:
                self.current_rotation_speed-=self.rotation_rate_of_change*0.5*time_passed
            else:
                self.rotation_change=0

        if self.rotation_change!=0:
            moved=True
            

            self.rotor_rotation+=(self.rotation_change*self.current_rotation_speed*time_passed)
            
        if self.vehicle!=None:
            if self.last_vehicle_position!=self.vehicle.world_coords:
                moved=True
                self.last_vehicle_position=copy.copy(self.vehicle.world_coords)
            elif self.last_vehicle_rotation!=self.vehicle.rotation_angle:
                moved=True
                self.last_vehicle_rotation=copy.copy(self.vehicle.rotation_angle)

        if moved:
            self.owner.reset_image=True
            if self.vehicle!=None:
                self.owner.rotation_angle=engine.math_2d.get_normalized_angle(self.vehicle.rotation_angle+self.rotor_rotation)
                self.owner.world_coords=engine.math_2d.calculate_relative_position(self.vehicle.world_coords,self.vehicle.rotation_angle,self.position_offset)


