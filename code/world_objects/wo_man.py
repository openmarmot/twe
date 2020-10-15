
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
from ai.ai_zombie import AIZombie
# module specific variables
module_version='0.0' #module software version
module_last_update_date='september 08 2020' #date of last update

#global variables

class WOMan(WorldObject):

    def __init__(self, world):
        super().__init__(world)
        self.image_name='russian_soldier'
        self.render_level=1
        self.ai=AIZombie(self)
