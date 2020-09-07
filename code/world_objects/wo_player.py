
'''
module : module_template.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages
from engine.world_object import WorldObject
from ai.ai_player import AIPlayer
# module specific variables
module_version='0.0' #module software version
module_last_update_date='Feb 07 2020' #date of last update

#global variables

class WOPlayer(WorldObject):

    def __init__(self, world):
        WorldObject.__init__(self, world, "man")
        self.image_name='man'
        self.render_level=1
        self.ai=AIPlayer(self)
