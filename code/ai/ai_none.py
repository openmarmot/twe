
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : default ai class for objects that don't use AI
'''

#import built in modules

#import custom packages

class AINone():
    def __init__(self, owner):
        self.owner=owner
    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''
        pass

    #---------------------------------------------------------------------------
