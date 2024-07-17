
'''
module : ai_turret.py
language : Python 3.x
email : andrew@openmarmot.com
notes : the turret for a tank, or the mg mount on a vehicle
'''

#import built in modules
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d


#global variables

class AITurret(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # offset to position it correctly on a vehicle. vehicle specific 
        self.position_offset=[0,0]

        # this is relative to the vehicle
        # really + or - a certain amount of degrees
        self.turret_rotation=0

        # gunner requested rotation change
        self.rotation_change=0

        self.rotation_range=[-20,20]

        # speed of rotation
        self.rotation_speed=20

        self.vehicle=None
        self.last_vehicle_position=[0,0]
        self.last_vehicle_rotation=0

        self.gunner=None # used to keep track of who is manning this turret

        # note - extra magazines/ammo should be stored in the vehicle inventory
        self.primary_weapon=None
        self.secondary_weapon=None


    #---------------------------------------------------------------------------
    def handle_rotate_left(self):
        self.rotation_change=1

    #---------------------------------------------------------------------------
    def handle_rotate_right(self):
        self.rotation_change=-1

    #---------------------------------------------------------------------------
    def handle_fire(self):
        self.primary_weapon.rotation_angle=self.owner.rotation_angle
        #self.primary_weapon.ai.fire()
        self.primary_weapon.ai.fire()

    #---------------------------------------------------------------------------
    def neutral_controls(self):
        ''' return controls to neutral over time'''

        if self.rotation_change!=0:
            # controls should return to neutral over time 
            time_passed=self.owner.world.graphic_engine.time_passed_seconds

            #return wheel to neutral
            self.rotation_change=engine.math_2d.regress_to_zero(self.rotation_change,time_passed)

    #---------------------------------------------------------------------------
    def update(self):

        if self.primary_weapon!=None:
            # needs updates for time tracking and other stuff
            self.primary_weapon.update()
        
        self.update_physics()

        self.neutral_controls()

    #---------------------------------------------------------------------------
    def update_physics(self):
        time_passed=self.owner.world.graphic_engine.time_passed_seconds
        moved=False

        if self.rotation_change!=0:
            moved=True
            self.turret_rotation+=(self.rotation_change*self.rotation_speed*time_passed)
            
            # make sure rotation is within bounds
            if self.turret_rotation<self.rotation_range[0]:
                self.turret_rotation=self.rotation_range[0]
                self.rotation_change=0
            elif self.turret_rotation>self.rotation_range[1]:
                self.turret_rotation=self.rotation_range[1]
                self.rotation_change=0

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
                self.owner.rotation_angle=engine.math_2d.get_normalized_angle(self.vehicle.rotation_angle+self.turret_rotation)
                self.owner.world_coords=engine.math_2d.calculate_relative_position(self.vehicle.world_coords,self.vehicle.rotation_angle,self.position_offset)


