
'''
module : ai_none.py
language : Python 3.x
email : andrew@openmarmot.com
notes : default ai class for objects that don't use AI
'''

#import built in modules

#import custom packages

class AINone(object):
    def __init__(self, owner):
        self.owner=owner
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        pass

    #---------------------------------------------------------------------------
