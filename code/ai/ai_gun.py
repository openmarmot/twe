
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

        # array of magazine objects
        self.magazines=[]

        
        #
        #time since last fired
        self.fire_time_passed=0. 

        # 60/rate of fire
        self.rate_of_fire=0.

        # reload speed in seconds
        self.reload_speed=10

        # time since reload started
        self.reload_time_passed=0

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

        # type pistol/rifle/semi auto rifle/submachine gun/assault rifle/machine gun
        self.type=''

        

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

        # note - ai human calls update for its primary weapon

        self.fire_time_passed+=self.owner.world.graphic_engine.time_passed_seconds

        if self.reloading:
            self.reload_time_passed+=self.owner.world.graphic_engine.time_passed_seconds
            if self.reload_time_passed>self.reload_speed:
                self.reloading=False
                self.reload_time_passed=0
                if self.equipper!=None:
                    if self.equipper.is_player:
                        self.equipper.ai.speak('[Reloading done. '+str(self.magazine_count)+' magazines left]')

    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    def change_magazine(self):
        ''' change magazine. input is new magazine. output is old magazine'''
        print('error: ai_gun change_magazine is not implemented')

    #---------------------------------------------------------------------------
    def fire(self,WORLD_COORDS,TARGET_COORDS):
        ''' fire the gun. returns True/False as to whether the gun fired '''
        fired=False
        # start with a time check
        if self.reloading==False:
            if(self.fire_time_passed>self.rate_of_fire):
                self.fire_time_passed=0.
                # start by ruling out empty mag 
                if self.magazine<1:
                    # auto reload ?
                    if self.equipper.is_player:
                        self.equipper.ai.speak('[Reloading !!]')
                    elif self.equipper.is_human:
                        self.equipper.ai.speak('Reloading !!')
                    if self.magazine_count>0:
                        self.magazine_count-=1
                        self.magazine=self.mag_capacity
                        self.reloading=True

                else :
                    fired=True
                    self.magazine-=1
                    self.rounds_fired+=1
                    spr=[random.randint(-self.spread,self.spread),random.randint(-self.spread,self.spread)]

                    ignore_list=[self.equipper]

                    if self.owner.world.friendly_fire==False:
                        if self.equipper.is_german:
                                ignore_list+=self.owner.world.wo_objects_german
                        elif self.equipper.is_soviet:
                            ignore_list+=self.owner.world.wo_objects_soviet
                        elif self.equipper.is_american:
                            ignore_list+=self.owner.world.wo_objects_american
                    elif self.owner.world.friendly_fire_squad==False:
                        # just add the squad
                        ignore_list+=self.equipper.ai.squad.members

                    if self.equipper.is_player:
                        pass
                    elif self.equipper.is_soldier:
                        pass
                    if self.equipper.ai.in_vehicle:
                        # add the vehicle otherwise it tends to get hit
                        ignore_list.append(self.equipper.ai.vehicle)

                    if self.equipper.ai.in_building:
                        # add possible buildings the equipper is in.
                        # assuming they are shooting out windows so should not hit the building
                        ignore_list+=self.equipper.ai.building_list

                    engine.world_builder.spawn_projectile(self.owner.world,WORLD_COORDS,TARGET_COORDS,spr,ignore_list,self.equipper,self.flight_time,self.projectile_type,self.owner.name)

                    # spawn brass 
                    engine.world_builder.spawn_object(self.owner.world,WORLD_COORDS,'brass',True)

        return fired

    #---------------------------------------------------------------------------
    def get_ammo_count(self):
        ''' get ammo count. should return int'''
        return self.magazine + (self.mag_capacity*self.magazine_count)      

#---------------------------------------------------------------------------
    def get_max_ammo_count(self):
        ''' get max ammo count. should return int'''
        return self.mag_capacity*self.max_magazines     


    #---------------------------------------------------------------------------
    def reload_current_mag(self):
        ''' reload the current magazine'''
        pass