
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
def get_vector_length(vec2):
	return math.sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])

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

#------------------------------------------------------------------------------
def get_normalized(vec2):
	l=math.sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])
	b=[0.,0.]
	try:
		b=[vec2[0]/l,vec2[1]/l]
	except ZeroDivisionError:
		pass
	return b 

#------------------------------------------------------------------------------
def moveTowardsTarget(speed,location,destination, time_passed):
	vec_to_dest=[destination[0]-location[0],destination[1]-location[1]]
	distance=get_vector_length(vec_to_dest)
	heading=get_normalized(vec_to_dest)
	travel_distance=min(distance,time_passed*speed)
	change=[heading[0]*travel_distance,heading[1]*travel_distance]
	return [location[0]+change[0],location[1]+change[1]]

