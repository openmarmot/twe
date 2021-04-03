
'''
module : ai_player.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d
# module specific variables
module_version='0.0' #module software version
module_last_update_date='Feb 07 2020' #date of last update

#global variables

class AIMan(AIBase):
    def __init__(self, owner):
        super().__init__(owner)

        self.primary_weapon=None
        self.throwable=None

    #---------------------------------------------------------------------------
    def update(self, time_passed):
        ''' overrides base update '''
        if(self.owner.is_player):
            self.handle_player(time_passed)
        else :
            # must be AI controlled
            pass

        
    #---------------------------------------------------------------------------
    def handle_event(self, EVENT, EVENT_DATA):
        ''' overrides base handle_event'''
        # not sure what to do here yet. will have to think of some standard events
        pass

    #---------------------------------------------------------------------------
    def handle_player(self,time_passed):
        ''' handle any player specific code'''

        if(self.owner.world.graphic_engine.keyPressed('w')):
            self.owner.world_coords[1]-=self.owner.speed*time_passed
            self.owner.rotation_angle=0
        if(self.owner.world.graphic_engine.keyPressed('s')):
            self.owner.world_coords[1]+=self.owner.speed*time_passed
            self.owner.rotation_angle=180
        if(self.owner.world.graphic_engine.keyPressed('a')):
            self.owner.world_coords[0]-=self.owner.speed*time_passed
            self.owner.rotation_angle=90
        if(self.owner.world.graphic_engine.keyPressed('d')):
            self.owner.world_coords[0]+=self.owner.speed*time_passed
            self.owner.rotation_angle=270
        if(self.owner.world.graphic_engine.keyPressed('f')):
            # fire the gun
            pass 
        if(self.owner.world.graphic_engine.keyPressed('g')):
            # throw throwable object
            pass 
