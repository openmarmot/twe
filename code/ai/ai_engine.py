
'''
module : ai_engine.py
Language : Python 3.x
email : andrew@openmarmot.com
notes : represents an engine. (car engine, jet engine, etc)
'''


#import built in modules

#import custom packages
from ai.ai_base import AIBase
import engine.math_2d

# this is for objects that don't need AI

#global variables

class AIEngine(AIBase):
    def __init__(self, owner):
        super().__init__(owner)
        
        # gas / diesel / jet fuel?
        self.fuel_type = None

        # fuel consumptuion as liters per second
        self.fuel_consumption_rate=0

        # amount of fuel the engine has consumed
        # vehicle uses this to pull fuel from the fuel tanks
        # vehicle will zero out when it pulls fuel
        self.fuel_consumed=0

        # amount of fuel the engine has internally (L)
        # basically the amount it can burn before running dry if not hooked up to a tank
        self.fuel_reservoir=1

        # bool. is the engine on or off ?
        self.engine_on=False

        self.installed_in_vehicle=False

        # basically controls rpm and fuel flow 0=no power 1= max power
        self.throttle_control=0

    #---------------------------------------------------------------------------
    def consume_fuel(self):
        if self.engine_on:
            self.fuel_consumed+=self.fuel_consumption_rate*self.throttle_control*self.owner.world.graphic_engine.time_passed_seconds

            if self.fuel_consumed>self.fuel_reservoir:
                # we are now out of fuel
                self.engine_on=False

            



    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        
        # probably excessive to run this every update. could add up fuel usage
        # and run it randomly instead
        self.consume_fuel

    #---------------------------------------------------------------------------
