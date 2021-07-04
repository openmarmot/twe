
'''
module : ai_gun.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
'''


#import built in modules
import random 

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
import engine.world_builder 

# module specific variables
module_version='0.0' #module software version
module_last_update_date='June 22 2021' #date of last update

#global variables

class AIGun(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        #int representing round count in current mag 
        self.magazine=0

        # the ammo capacity of a magazine for this weapon
        # for example a mp40 would be 32
        self.mag_capacity=0
        
        # how many full mags you have
        self.magazine_count=0

        # max full mags you can have 
        self.max_magazines=0
        
        #
        #time since last fired
        self.fire_time_passed=0. 

        # fire rate in seconds?
        self.rate_of_fire=0.

        # caliber

        # bullet diameter in mm
        self.bullet_diameter=0
        
        # bullet weight
        self.bullet_weight=0

        # muzzle velocity
        self.muzzle_velocity=0

        # spread
        self.spread=15

        # internal counter of rounds fired
        self.rounds_fired=0

        # the object (human) that actually equipped this weapon
        # set by ai_man.event_inventory
        self.equipper=None

        # type pistol/rifle/semi auto rifle/submachine gun/assault rifle/machine gun
        self.type=''

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        self.fire_time_passed+=self.owner.world.graphic_engine.time_passed_seconds
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def change_magazine(self):
        ''' change magazine. input is new magazine. output is old magazine'''
        pass

    #---------------------------------------------------------------------------
    def fire(self,WORLD_COORDS,TARGET_COORDS):
        ''' fire the gun '''

  
        # start with a time check
        if(self.fire_time_passed>self.rate_of_fire):
            self.fire_time_passed=0.
            # start by ruling out empty mag 
            if self.magazine<1:
                # auto reload ?
                if self.equipper.is_player:
                    print("magazine empty")
                if self.magazine_count>0:
                    self.magazine_count-=1
                    self.magazine=self.mag_capacity
                    if self.equipper.is_player:
                        print(" Remaining magazines: "+str(self.magazine_count)+ '  Rounds fired '+str(self.rounds_fired))
                else:
                    print(self.equipper.name + ' out of ammo for ' + self.owner.name + ' Rounds fired '+str(self.rounds_fired))

                    if self.equipper.is_player:
                        print(' out of ammo for ' + self.owner.name + ' Rounds fired '+str(self.rounds_fired))
            else :
                self.magazine-=1
                self.rounds_fired+=1
                spr=[random.randint(-self.spread,self.spread),random.randint(-self.spread,self.spread)]
                if self.equipper.is_player:
                    engine.world_builder.spawn_projectile(self.owner.world,WORLD_COORDS,TARGET_COORDS,spr,[self.equipper],True,self.equipper)
                elif self.equipper.is_soldier:
                    # squad gets added to make immune to friendly fire
                    engine.world_builder.spawn_projectile(self.owner.world,WORLD_COORDS,TARGET_COORDS,spr,self.equipper.ai.squad.members,False,self.equipper)
                else:
                    engine.world_builder.spawn_projectile(self.owner.world,WORLD_COORDS,TARGET_COORDS,spr,[self.equipper],False,self.equipper)

                # spawn brass 
                engine.world_builder.spawn_sprite(self.owner.world,WORLD_COORDS,'brass')

        


    #---------------------------------------------------------------------------
    def reload_current_mag(self):
        ''' reload the current magazine'''
        pass