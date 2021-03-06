
'''
module : math_2d.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes : 

static module consisting of math functions.
import as needed

# ref
# notes on som differenct collisiong algos
# https://www.h3xed.com/programming/bounding-box-vs-bounding-circle-collision-detection-performance-as3#:~:text=%2F%2F%20Collision!,-%7D&text=The%20above%20run%20took%20164,the%20nature%20of%20your%20game.
'''


#import built in modules
import math
#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='April 10 2021' #date of last update

#global variables

#------------------------------------------------------------------------------
def checkCollisionSquareOneResult(wo, collision_list, ignore_list):
	# wo - (worldobject)the object possibly doing the colliding 
	# collision_list - (list[worldobject] a list of all possible objects that 
	# list of objects to ignore
	# could be collided with

	# checks collision based on a bounding box style check where the box is made
	# with the collision radius (so its a square)

	# returns the first result only

	collided=None
	for b in collision_list:
		if wo.world_coords[0]+wo.collision_radius > b.world_coords[0]:
			if wo.world_coords[0] < b.world_coords[0]+b.collision_radius:
				if wo.world_coords[1]+wo.collision_radius > b.world_coords[1]:
					if wo.world_coords[1] < b.world_coords[1]+b.collision_radius:
						if wo!=b and (b not in ignore_list):
							collided=b
							break
	return collided

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
def get_heading_vector(location,destination):
	''' normalized vector representing the heading (direction) to a target'''
	# location = [float,float]
	# destination = [float,float]
	vec_to_dest=[destination[0]-location[0],destination[1]-location[1]]
	heading=get_normalized(vec_to_dest)
	return heading 

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
def moveAlongVector(speed,location,heading,time_passed):
	''' returns a location vector that has been moved along a heading vector'''
	travel_distance=speed*time_passed
	change=[heading[0]*travel_distance,heading[1]*travel_distance]
	return [location[0]+change[0],location[1]+change[1]]


#------------------------------------------------------------------------------
def moveTowardsTarget(speed,location,destination, time_passed):
	vec_to_dest=[destination[0]-location[0],destination[1]-location[1]]
	distance=get_vector_length(vec_to_dest)
	heading=get_normalized(vec_to_dest)
	# basically takes the minimum of distance or travel so as not to go past the target
	travel_distance=min(distance,time_passed*speed)
	change=[heading[0]*travel_distance,heading[1]*travel_distance]
	return [location[0]+change[0],location[1]+change[1]]





