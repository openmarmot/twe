
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
        self.turret_rotation=0

        self.vehicle=None
        self.last_vehicle_position=[0,0]
        self.last_vehicle_rotation=0

        # note - extra magazines/ammo should be stored in the vehicle inventory
        self.primary_weapon=None
        self.secondary_weapon=None
    #---------------------------------------------------------------------------
    def update(self):
        
        self.update_physics()

    #---------------------------------------------------------------------------
    def update_physics(self):
        moved=False

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


