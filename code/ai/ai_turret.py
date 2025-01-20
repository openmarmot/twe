
'''
module : ai_turret.py
language : Python 3.x
email : andrew@openmarmot.com
notes : the turret for a tank, or the mg mount on a vehicle
'''

#import built in modules
import copy

#import custom packages
import engine.math_2d
import engine.log
import engine.penetration_calculator
import random


#global variables

class AITurret(object):
    def __init__(self, owner):
        self.owner=owner

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
        self.turret_jammed=False

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


        # note - extra magazines/ammo should be stored in the vehicle inventory
        self.primary_weapon=None
        self.coaxial_weapon=None

    #---------------------------------------------------------------------------
    def calculate_accuracy(self,weapon):
        temp_heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
        far_coords=engine.math_2d.moveAlongVector(1000,self.owner.world_coords,temp_heading,1)

        adjust_max=0
        adjust_max+=weapon.ai.mechanical_accuracy

        if self.vehicle.ai.current_speed>0:
            adjust_max+=10
        if self.vehicle.ai.current_speed>100:
            adjust_max+=10

        # apply adjustment
        far_coords=[far_coords[0]+random.uniform(-adjust_max,adjust_max),far_coords[1]+random.uniform(-adjust_max,adjust_max)]

        # get the new angle 
        return engine.math_2d.get_rotation(self.owner.world_coords,far_coords)


    #---------------------------------------------------------------------------
    def event_collision(self,EVENT_DATA):
        

        if EVENT_DATA.is_projectile:
            projectile=EVENT_DATA
            distance=engine.math_2d.get_distance(self.owner.world_coords,projectile.ai.starting_coords,True)

            side=engine.math_2d.calculate_hit_side(self.owner.rotation_angle,projectile.rotation_angle)
            penetration=engine.penetration_calculator.calculate_penetration(projectile,distance,'steel',self.turret_armor[side])
            if self.vehicle!=None:
                self.vehicle.ai.add_hit_data(projectile,penetration,side,distance,'Turret')
            if penetration:
                if self.vehicle!=None:
                    # remote operated turrets mean that the gunner can't be hit by turret penetrations 
                    if self.remote_operated==False:
                        if random.randint(0,1)==1:
                            for key,value in self.vehicle.ai.vehicle_crew.items():
                                if value[5]==self.owner:
                                    if value[0]==True:
                                        value[1].ai.handle_event('collision',projectile)

                    # chance to essentially ricochet/explode/shrapnel down into the main vehicle
                    if random.randint(0,2)==2:
                        self.vehicle.ai.health-=random.randint(20,30)
                        # should have a chance to damage crew as well
                
                # should do component damage here
                if random.randint(0,1)==1:
                    self.turret_jammed=True
                else:
                    self.health-=random.randint(25,75)

            else:
                # bounced the projectile
                pass

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
        if self.turret_jammed is False:
            self.rotation_change=1

    #---------------------------------------------------------------------------
    def handle_rotate_right(self):
        if self.turret_jammed is False:
            self.rotation_change=-1

    #---------------------------------------------------------------------------
    def handle_fire(self):
        if self.health>0:
            if self.primary_weapon.ai.check_if_can_fire():
                self.primary_weapon.rotation_angle=self.calculate_accuracy(self.primary_weapon)
                self.primary_weapon.ai.fire()

    #---------------------------------------------------------------------------
    def handle_fire_coax(self):
        if self.health>0:
            if self.coaxial_weapon.ai.check_if_can_fire():
                self.coaxial_weapon.rotation_angle=self.calculate_accuracy(self.coaxial_weapon)
                self.coaxial_weapon.ai.fire()

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


