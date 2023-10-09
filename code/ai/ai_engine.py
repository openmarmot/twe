
'''
module : ai_engine.py
Language : Python 3.x
email : andrew@openmarmot.com
notes : represents an engine. (car engine, jet engine, etc)
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase

# this is for objects that don't need AI

#global variables

class AIEngine(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        
        # gas / diesel / jet fuel?
        self.fuel_type = None

        # fuel consumptuion as liters per second
        self.fuel_consumption=0

        # bool. is the engine on or off ?
        self.engine_on=False

        self.installed_in_vehicle=False

        # vehicle that the engine is installed in 
        self.vehicle=None

    #---------------------------------------------------------------------------
    def consume_fuel(self):
        if self.engine_on:
            self.fuel-=self.fuel_consumption*self.owner.world.graphic_engine.time_passed_seconds

            if self.throttle>0.5:
                #essentially double fuel consumption
                self.fuel-=self.fuel_consumption*self.owner.world.graphic_engine.time_passed_seconds

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
