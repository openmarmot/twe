
'''
module : ai_gun.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import random
import copy

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder 
import engine.penetration_calculator


#global variables

class AIGun(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        # The magazine that is loaded in the gun
        self.magazine=None

        #time since last fired
        self.fire_time_passed=0. 

        # 60/rate of fire
        self.rate_of_fire=0.

        # reload speed in seconds
        self.reload_speed=10

        # bool
        self.reloading=False

        # bullet diameter in mm (not used. yet!)
        self.bullet_diameter=0

        # muzzle velocity (not used)
        self.muzzle_velocity=0

        # flight time - basically how long the bullet will stay in the air 
        self.flight_time=0

        # range - estimate of the distance a gun can hit out to. used by bot ai 
        self.range=0

        # spread
        self.spread=15

        # internal counter of rounds fired
        self.rounds_fired=0

        # the object (human) that actually equipped this weapon
        # set by ai_man.event_inventory
        self.equipper=None

        # type pistol/rifle/semi auto rifle/submachine gun/assault rifle/machine gun/antitank launcher
        self.type=''

        # spawns smoke when fired
        self.smoke_on_fire=False

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # note - ai human calls update for its primary weapon

        self.fire_time_passed+=self.owner.world.graphic_engine.time_passed_seconds

    #---------------------------------------------------------------------------
    def fire(self,world_coords,target_coords):
        ''' fire the gun. returns True/False as to whether the gun fired '''
        fired=False
        # check that we have a magazine loaded
        if self.magazine!=None:
            # check fire rate hasn't been exceeded
            if(self.fire_time_passed>self.rate_of_fire):
                self.fire_time_passed=0.
                # start by ruling out empty mag 
                
                # if we have bullets left
                if len(self.magazine.ai.projectiles)>0:
                    fired=True
                    projectile=self.magazine.ai.projectiles.pop()
                    self.rounds_fired+=1
                    spread=[random.randint(-self.spread,self.spread),random.randint(-self.spread,self.spread)]

                    projectile.ai.weapon_name=self.owner.name
                    projectile.ai.shooter=self.equipper
                    projectile.ai.ignore_list=self.owner.world.generate_ignore_list(self.equipper)
                    projectile.world_coords=copy.copy(self.equipper.world_coords)
                    projectile.ai.starting_coords=copy.copy(self.equipper.world_coords)
                    projectile.ai.maxTime=self.flight_time + random.uniform(0.01, 0.05)
                    
                    if self.equipper.is_player :
                        # do computations based off of where the mouse is. TARGET_COORDS is ignored
                        dst=self.owner.world.graphic_engine.get_mouse_screen_coords()
                        dst=[dst[0]+spread[0],dst[1]+spread[1]]
                        projectile.rotation_angle=engine.math_2d.get_rotation(self.owner.world.graphic_engine.get_player_screen_coords(),dst)
                        projectile.heading=engine.math_2d.get_heading_vector(self.owner.world.graphic_engine.get_player_screen_coords(),dst)
                    else :
                        dst=[target_coords[0]+spread[0],target_coords[1]+spread[1]]
                        projectile.rotation_angle=engine.math_2d.get_rotation(world_coords,dst)
                        projectile.heading=engine.math_2d.get_heading_vector(world_coords,dst)

                    self.owner.world.add_queue.append(projectile)

                    # spawn smoke
                    if self.smoke_on_fire:
                        heading=engine.math_2d.get_heading_from_rotation(self.equipper.rotation_angle+180)
                        engine.world_builder.spawn_smoke_cloud(self.owner.world,self.equipper.world_coords,heading)

                    # spawn bullet case
                    if engine.penetration_calculator.projectile_data[projectile.ai.projectile_type]['case_material']=='steel':
                        z=engine.world_builder.spawn_object(self.owner.world,world_coords,'steel_case',True)
                        z.heading=engine.math_2d.get_heading_from_rotation(projectile.rotation_angle-90)
                    elif engine.penetration_calculator.projectile_data[projectile.ai.projectile_type]['case_material']=='brass':
                        z=engine.world_builder.spawn_object(self.owner.world,world_coords,'brass',True)
                        z.heading=engine.math_2d.get_heading_from_rotation(projectile.rotation_angle-90)

        return fired



