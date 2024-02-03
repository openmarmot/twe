
'''
module : ai_coffee_grinder.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.world_builder


# this is for objects that don't need AI

#global variables

class AICoffeeGrinder(AIBase):
    def __init__(self, owner):
        super().__init__(owner)


    #---------------------------------------------------------------------------
    def grind(self,obj_to_grind):
        ''' takes obj_to_grind as input, returns the resulting object'''
        z=None

        if obj_to_grind.name=='coffee_beans':
            z=engine.world_builder.spawn_object(self.owner.world,[0,0],'ground_coffee',False)
            z.volume=obj_to_grind.volume
            z.weight=obj_to_grind.weight
        else:
            print('Warn - attempting to grind unhandled material: ',obj_to_grind.name)

        return z

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
