
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import random
import copy

#import custom packages
import engine.math_2d
import engine.world_builder 
import engine.penetration_calculator


#global variables

class AIGun(object):
    def __init__(self, owner):
        self.owner=owner

        # The magazine that is loaded in the gun
        self.magazine=None

        #time last fired
        self.last_fired_time=0

        # 60/(rate of fire in rounds per minute)
        self.rate_of_fire=0.

        # time in seconds it takes to reload
        # this is referenced by ai_human
        self.reload_speed=15

        # bullet diameter in mm (not used. yet!)
        self.bullet_diameter=0

        # muzzle velocity
        # this is in game units and sets the projectile speed
        # max currently is 1000
        self.muzzle_velocity=1000

        # mechanical accuracy from a stable mount. 0 is perfectly accurate
        # 0 is perfect. 5 is terrible
        # most rifles are 1
        self.mechanical_accuracy=0

        # range - how far the bullet will go before hitting the ground
        # used by the ai and used to calculate projectile flight time
        self.range=0

        # spread
        #self.spread=15

        # internal counter of rounds fired
        self.rounds_fired=0
        self.rounds_hit=0

        # the object that actually equipped this weapon. either a turret or a human
        # set by ai_man.event_inventory or worldbuilder for turrets
        self.equipper=None

        # type pistol/rifle/semi auto rifle/submachine gun/assault rifle/machine gun/antitank launcher
        self.type=''

        # spawns smoke when fired
        self.smoke_on_fire=False
        self.smoke_type='none'
        self.smoke_offset=[0,0]

        # spawn a bullet casing when fired
        self.spawn_case=True

        # gives the AI hints on how to use this weapon
        self.use_antitank=False
        self.use_antipersonnel=False

        self.damaged=False # gun is damaged and cannot operate
        self.action_jammed=False # gun action is jammed witha shell in the chamber


        # what type of fire mode the weapon supports
        self.direct_fire=True
        self.indirect_fire=False

    #---------------------------------------------------------------------------
    def check_if_can_fire(self):
        '''bool as to whether the gun can fire'''
        ''' used externally and by the fire function'''
        if self.damaged or self.action_jammed:
            return False

        if self.magazine!=None:
            if(self.owner.world.world_seconds-self.last_fired_time>self.rate_of_fire):
                if len(self.magazine.ai.projectiles)>0:
                    return True
        
        return False
    
    #---------------------------------------------------------------------------
    def fire(self):
        ''' fire the gun. run check_if_can_fire first if you have calculations to do'''
        if self.check_if_can_fire():
            self.last_fired_time=self.owner.world.world_seconds
            projectile=self.magazine.ai.projectiles.pop()
            self.rounds_fired+=1
            
            projectile.ai.weapon=self.owner
            projectile.ai.shooter=self.equipper
            projectile.ai.ignore_list=self.owner.world.generate_ignore_list(self.equipper)
            projectile.world_coords=copy.copy(self.equipper.world_coords)
            projectile.ai.starting_coords=copy.copy(self.equipper.world_coords)
            projectile.ai.maxTime=self.range/projectile.ai.speed
            projectile.rotation_angle=self.owner.rotation_angle
            projectile.heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
            projectile.ai.speed=self.muzzle_velocity
            
            self.owner.world.add_queue.append(projectile)

            # spawn smoke
            if self.smoke_on_fire:
                if self.smoke_type=='rocket':
                    heading=engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,self.equipper.world_coords,heading)
                    coords=engine.math_2d.moveAlongVector(-15,self.equipper.world_coords,heading,1)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,coords,heading)
                    coords=engine.math_2d.moveAlongVector(-15,coords,heading,1)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,coords,heading)
                    coords=engine.math_2d.moveAlongVector(-15,coords,heading,1)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,coords,heading)
                elif self.smoke_type=='cannon':
                    left_heading=engine.math_2d.get_heading_from_rotation(
                        engine.math_2d.get_normalized_angle(self.owner.rotation_angle-90))
                    right_heading=engine.math_2d.get_heading_from_rotation(
                        engine.math_2d.get_normalized_angle(self.owner.rotation_angle+90))
                    coords=engine.math_2d.calculate_relative_position(
                        self.equipper.world_coords,self.owner.rotation_angle,self.smoke_offset)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,coords,left_heading,3)
                    engine.world_builder.spawn_smoke_cloud(self.owner.world,coords,right_heading,3)
                    engine.world_builder.spawn_flash(self.owner.world,coords,
                        engine.math_2d.get_heading_from_rotation(self.owner.rotation_angle))

            # spawn bullet case
            if self.spawn_case:
                if engine.penetration_calculator.projectile_data[projectile.ai.projectile_type]['case_material']=='steel':
                    z=engine.world_builder.spawn_object(self.owner.world,self.equipper.world_coords,'steel_case',True)
                    z.heading=engine.math_2d.get_heading_from_rotation(projectile.rotation_angle-90)
                elif engine.penetration_calculator.projectile_data[projectile.ai.projectile_type]['case_material']=='brass':
                    z=engine.world_builder.spawn_object(self.owner.world,self.equipper.world_coords,'brass',True)
                    z.heading=engine.math_2d.get_heading_from_rotation(projectile.rotation_angle-90)

            # handle special case for weapons that change appearance when empty
            if len(self.magazine.ai.projectiles)==0:
                if 'panzerfaust' in self.owner.name:
                    self.owner.image_index=1

    #---------------------------------------------------------------------------
    def get_accuracy(self):
        '''get the accuracy of the weapon'''

        if self.rounds_fired==0:
            return "0.0%"
        return f'{round(self.rounds_hit/self.rounds_fired,1)*100}%'

    #---------------------------------------------------------------------------
    def update(self):
        '''update'''
        pass

