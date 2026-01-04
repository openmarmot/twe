
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : a wearable is a piece of clothing armor, etc. something you can wear
'''

#import built in modules

#import custom packages

# this is for objects that don't need AI

#global variables

class AIWearable():
    def __init__(self, owner):
        self.owner=owner
        # head / whatever
        self.wearable_region='none'
        #[side][armor thickness,armor slope,spaced_armor_thickness]
        # slope 0 degrees is vertical, 90 degrees is horizontal
        self.armor={}
        self.armor['top']=[0,0,0]
        self.armor['bottom']=[0,0,0]
        self.armor['left']=[0,0,0]
        self.armor['right']=[0,0,0]
        self.armor['front']=[0,0,0]
        self.armor['rear']=[0,0,0]

    #---------------------------------------------------------------------------
    def update(self):
        ''' overrides base update '''

    #---------------------------------------------------------------------------
