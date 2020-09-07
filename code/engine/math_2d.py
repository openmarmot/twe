
'''
module : ai_base.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :

static module consisting of math functions.
import as needed

'''


#import built in modules
import math
#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='July 02 2016' #date of last update

#global variables

#------------------------------------------------------------------------------
def get_rotation(coords, target_coords):
	delta_x=coords[0]-target_coords[0]
	delta_y=coords[1]-target_coords[1]
	return math.atan2(delta_x,delta_y) *180 / math.pi

#------------------------------------------------------------------------------

def get_distance(coords1, coords2):
	x=coords1[0]-coords2[0]
	y=coords1[1]-coords2[1]
	return math.sqrt(x*x+y*y)
