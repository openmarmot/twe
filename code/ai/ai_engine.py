
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

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
