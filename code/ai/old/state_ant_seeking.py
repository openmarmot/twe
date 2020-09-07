
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


class AntStateSeeking(State):

    def __init__(self, ant):

        State.__init__(self, "seeking")
        self.ant = ant
        self.leaf_id = None

    def check_conditions(self):

        leaf = self.ant.world.get(self.ant.leaf_id)
        if leaf is None:
            return "exploring"

        if self.ant.location.get_distance_to(leaf.location) < 5:

            self.ant.carry(self.ant.world.graphic_engine.images['cat grass'])
            self.ant.world.remove_entity(leaf)
            return "delivering"

        return None

    def entry_actions(self):

        leaf = self.ant.world.get(self.ant.leaf_id)
        if leaf is not None:
            self.ant.destination = leaf.location
            self.ant.speed = 160 + randint(-20, 20)
