
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
import engine.log
import engine.penetration_calculator
import random


#global variables

class AITurret(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        #[side][armor thickness,armor slope,spaced_armor_thickness]
        # slope 0 degrees is vertical, 90 degrees is horizontal
        # armor grade steel thickness in mm. standard soft aluminum/steel is a 0-1
        self.turret_armor={}
        self.turret_armor['top']=[0,0,0]
        self.turret_armor['bottom']=[0,0,0]
        self.turret_armor['left']=[0,0,0]
        self.turret_armor['right']=[0,0,0]
        self.turret_armor['front']=[0,0,0]
        self.turret_armor['rear']=[0,0,0]

        self.health=100

        # for remote operated machine guns - mostly german
        self.remote_operated=False

        # offset to position it correctly on a vehicle. vehicle specific 
        self.position_offset=[0,0]

        # this is relative to the vehicle
        # really + or - a certain amount of degrees
        self.turret_rotation=0

        # gunner requested rotation change
        self.rotation_change=0

        # rotation range for the turret
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

        self.collision_log=[]

    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        

        if EVENT_DATA.is_projectile:
            projectile=EVENT_DATA
            distance=engine.math_2d.get_distance(self.owner.world_coords,projectile.ai.starting_coords,True)

            side=engine.math_2d.calculate_hit_side(self.owner.rotation_angle,projectile.rotation_angle)
            penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.turret_armor[side])

            if penetration:
                self.collision_log.append('[penetration] Turret hit by '+projectile.ai.projectile_type + 
                    ' on the '+side+' at a distance of '+ str(distance))
                # remote operated turrets mean that the gunner can't be hit by turret penetrations 
                if self.gunner!=None and self.remote_operated==False:
                    if random.randint(0,2)==2:
                        self.gunner.ai.handle_event('collision',projectile)
                
                # should do component damage here
                self.health-=random.randint(1,25)

            else:
                # no penetration, but maybe we can have some other effect?
                self.collision_log.append('[bounce] Turret hit by '+projectile.ai.projectile_type + 
                     ' on the '+side+' at a distance of '+ str(distance))

        elif EVENT_DATA.is_grenade:
            print('bonk')
        else:
            engine.log.add_data('error','ai_vehicle event_collision - unhandled collision type'+EVENT_DATA.name,True)

    #---------------------------------------------------------------------------
    def handle_event(self, event, event_data):
        ''' overrides base handle_event'''
        # EVENT - text describing event
        # event_data - most likely a world_object but could be anything

        # not sure what to do here yet. will have to think of some standard events
        if event=='add_inventory':
            engine.log.add_data('Error','ai_turret handle_event add_inventory not implemented',True)
            #self.event_add_inventory(event_data)
        elif event=='collision':
            self.event_collision(event_data)
        elif event=='remove_inventory':
            engine.log.add_data('Error','ai_turret handle_event remove_inventory not implemented',True)
            #self.event_remove_inventory(event_data)
        else:
            print('Error: '+self.owner.name+' cannot handle event '+event)

    #---------------------------------------------------------------------------
    def handle_rotate_left(self):
        self.rotation_change=1

    #---------------------------------------------------------------------------
    def handle_rotate_right(self):
        self.rotation_change=-1

    #---------------------------------------------------------------------------
    def handle_fire(self):
        if self.health>0:
            self.primary_weapon.rotation_angle=self.owner.rotation_angle
            self.primary_weapon.ai.fire()

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

        if self.primary_weapon!=None:
            # needs updates for time tracking and other stuff
            self.primary_weapon.update()
        
        self.update_physics()

        self.neutral_controls()

    #---------------------------------------------------------------------------
    def update_physics(self):
        time_passed=self.owner.world.time_passed_seconds
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


