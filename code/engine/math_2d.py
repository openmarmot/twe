
'''
module : math_2d.py
version : see module_version variable
Language : Python 3.x
email : andrew@openmarmot.com
notes : 

static module consisting of math functions.
import as needed

I'm pretty sure something is fundamentally wrong with my math in this game 
some of these functions are the opposite of what they should be
lets just pretend this is all sane. super sane

# ref
# notes on som differenct collisiong algos
# https://www.h3xed.com/programming/bounding-box-vs-bounding-circle-collision-detection-performance-as3#:~:text=%2F%2F%20Collision!,-%7D&text=The%20above%20run%20took%20164,the%20nature%20of%20your%20game.
# more notes - similar 
# https://developer.mozilla.org/en-US/docs/Games/Techniques/2D_collision_detection
'''


#import built in modules
import math
import random
#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='may23 2021' #date of last update

#global variables

#------------------------------------------------------------------------------
def checkCollisionCircleMouse(MOUSE_COORDS, RADIUS, COLLISION_LIST):
	''' collision check modified for mouse screen coords'''
	# modified collision check for screen coords 
	# radius is used for both objects because screen coords perspective 
	# is scaled based on zoom 
	# called by world.select_with_mouse at the moment

	collided=None
	for b in COLLISION_LIST:

		distance=get_distance(MOUSE_COORDS,b.screen_coords)

		if distance < (RADIUS*2):
			collided=b
			break
	return collided


#------------------------------------------------------------------------------
def checkCollisionCircleOneResult(wo, collision_list, ignore_list):
	# wo - (worldobject)the object possibly doing the colliding 
	# collision_list - (list[worldobject] a list of all possible objects that 
	# list of objects to ignore (should include wo)

	# returns the first result only


	collided=None
	for b in collision_list:

		distance=get_distance(wo.world_coords,b.world_coords)

		if distance < (wo.collision_radius+b.collision_radius):
			if wo!=b and (b not in ignore_list):
				collided=b
				break
	return collided

#-----------------------------------------------------------------------------
def collision_sort(RUNS,WO_OBJECTS):
	''' moves around objects so they no longer collide'''
	# RUNS - number of runs through the resort algo you want to do. probably >100
	# WO_OBJECTS - list of objects to sort
	for x in range(RUNS):
		for a in WO_OBJECTS:
			if checkCollisionCircleOneResult(a,WO_OBJECTS,[a]) !=None:
                #collided. lets move the building in a super intelligent way
				a.world_coords[0]+=float(random.randint(-100,100))
				a.world_coords[1]+=float(random.randint(-100,100))

# #------------------------------------------------------------------------------
# def checkCollisionSquareOneResult(wo, collision_list, ignore_list):
# 	# wo - (worldobject)the object possibly doing the colliding 
# 	# collision_list - (list[worldobject] a list of all possible objects that 
# 	# list of objects to ignore (should include wo)
# 	# 

# 	# checks collision based on a bounding box style check where the box is made
# 	# with the collision radius (so its a square)

# 	# returns the first result only

# 	# !!! NOTE - this has a big error. this is meant to use width and height
# 	#  instead it uses radius twice - resulting in errors 

# 	collided=None
# 	for b in collision_list:
# 		if wo.world_coords[0]+wo.collision_radius > b.world_coords[0]:
# 			if wo.world_coords[0] < b.world_coords[0]+b.collision_radius:
# 				if wo.world_coords[1]+wo.collision_radius > b.world_coords[1]:
# 					if wo.world_coords[1] < b.world_coords[1]+b.collision_radius:
# 						if wo!=b and (b not in ignore_list):
# 							collided=b
# 							break
# 	return collided

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

#--------------------------------------------------------------------------------
def get_heading_from_rotation(ROTATION):
	''' get heading vector. input is rotation in degrees'''

	r=math.radians(ROTATION)
	b=[math.degrees(-math.sin(r)),-math.degrees(math.cos(r))]
	return get_normalized(b)

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





