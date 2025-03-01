
'''
module : ai_engine.py
Language : Python 3.x
email : andrew@openmarmot.com
notes : represents an engine. (car engine, jet engine, etc)
'''


#import built in modules

#import custom packages
import engine.math_2d

# this is for objects that don't need AI

#global variables

class AIEngine(object):
    def __init__(self, owner):
        self.owner=owner
        
        # internal combustion engine
        self.internal_combustion=True

        # list of acceptable fuels
        self.fuel_type = []

        # this is going to be vehicle specific
        self.exhaust_position_offset=[0,0]

        # fuel consumptuion as liters per second
        self.fuel_consumption_rate=0

        # idle fuel consumption rate when throttle is at zero
        self.idle_fuel_consumption_rate=0.001

        # amount of fuel the engine has consumed
        # vehicle uses this to pull fuel from the fuel tanks
        # vehicle will zero out when it pulls fuel
        self.fuel_consumed=0

        # amount of fuel the engine has internally (L)
        # basically the amount it can burn before running dry if not hooked up to a tank
        self.fuel_reservoir=1

        # bool. is the engine on or off ?
        self.engine_on=False

        # engine force in watts 
        # engine_force = (horsepower * 745.7) / 0.7375
        # 1 hp = 745.7 Watts
        self.max_engine_force=0

        # basically controls rpm and fuel flow 0=no power 1= max power
        # once the mechanism is in place to control this it should start at 0.
        # if its at 0 and the engine is on, the engine should choke and die
        self.throttle_control=1

        self.damaged=False

    #---------------------------------------------------------------------------
    def consume_fuel(self):
        if self.engine_on:
            if self.throttle_control>0:
                self.fuel_consumed+=self.fuel_consumption_rate*self.throttle_control*self.owner.world.time_passed_seconds
            else:
                self.fuel_consumed+=self.idle_fuel_consumption_rate*self.owner.world.time_passed_seconds

            if self.fuel_consumed>self.fuel_reservoir:
                # we are now out of fuel
                self.engine_on=False


    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        
        # probably excessive to run this every update. could add up fuel usage
        # and run it randomly instead
        if self.internal_combustion:
            self.consume_fuel()

    #---------------------------------------------------------------------------
