
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules
from random import randint, choice
#import custom packages
from ai.state import State
from engine.vector2 import Vector2
# module specific variables
module_version='0.0' #module software version
module_last_update_date='June 13 2016' #date of last update

#global variables


class AntStateDelivering(State):

    def __init__(self, ant):

        State.__init__(self, "delivering")
        self.ant = ant


    def check_conditions(self):

        if Vector2(*self.ant.world.NEST_POSITION).get_distance_to(self.ant.location) < self.ant.world.NEST_SIZE:
            if (randint(1, 10) == 1):
                self.ant.drop()
                return "exploring"

        return None


    def entry_actions(self):

        self.ant.speed = 60.
        random_offset = Vector2(randint(-20, 20), randint(-20, 20))
        self.ant.destination = Vector2(*self.ant.world.NEST_POSITION) + random_offset
