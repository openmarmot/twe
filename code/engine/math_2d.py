
'''
module : math_2d.py
language : Python 3.x
email : andrew@openmarmot.com
notes : 

static module consisting of math functions.

this started out as just 2d graphics math but it grew to have other functions.

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


#global variables

# constants (should be all caps as per pep8)
# velocity of gravity in meters/second
GRAVITY=-9.8


#------------------------------------------------------------------------------
def calculate_acceleration(force,rolling_resistance,drag_coefficient,air_density,frontal_area,weight):
	'''calculate acceleration'''
	# force - force in watts
	# rolling_resistance : maybe 0.015 for a jeep (1.5% of the vehicle weight)
	# drag_coefficient : maybe 0.8 for a jeep
	# air_density is the air density in kg/m^3 (typically around 1.225 kg/m^3 at sea level)
	# frontal_area is the objects frontal cross-sectional area in square meters
	# weight : kilograms

	# adjustment to game units 
	adjustment=1

	# Calculate net force
	net_force = force - (rolling_resistance * weight) - (0.5 * air_density * frontal_area * drag_coefficient)

	# Calculate acceleration in m/s^2
	acceleration = net_force / weight

	# adjust to game units 
	acceleration*=adjustment

	# round to 2 sd
	acceleration=round(acceleration,2)

	return acceleration


#------------------------------------------------------------------------------
def checkCollisionCircleMouse(mouse_coords, radius, collision_list):
	''' collision check modified for mouse screen coords'''
	# modified collision check for screen coords 
	# radius is used for both objects because screen coords perspective 
	# is scaled based on zoom 
	# called by world.select_with_mouse at the moment

	collided=None
	for b in collision_list:

		distance=get_distance(mouse_coords,b.screen_coords)

		if distance < (radius*2):
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
def collision_sort(runs,wo_objects):
	''' moves around objects so they no longer collide'''
	# RUNS - number of runs through the resort algo you want to do. probably >100
	# WO_OBJECTS - list of objects to sort
	for x in range(runs):
		for a in wo_objects:
			if checkCollisionCircleOneResult(a,wo_objects,[a]) !=None:
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
def get_distance(coords1, coords2,round_number=False):
	x=coords1[0]-coords2[0]
	y=coords1[1]-coords2[1]
	distance=math.sqrt(x*x+y*y)
	if round_number:
		return round(distance,1)
	else:
		return distance
	


#------------------------------------------------------------------------------
def get_heading_vector(location,destination):
	''' normalized vector representing the heading (direction) to a target'''
	# location = [float,float]
	# destination = [float,float]
	vec_to_dest=[destination[0]-location[0],destination[1]-location[1]]
	heading=get_normalized(vec_to_dest)
	return heading 

#--------------------------------------------------------------------------------
def get_heading_from_rotation(rotation):
	''' get heading vector. input is rotation in degrees'''

	r=math.radians(rotation)
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
def get_optimal_column_count(AMOUNT):
	'''calculates an optimal column count that balances columns and rows'''

	run=True
	columns=10
	while run :
		rows=AMOUNT/columns
		if rows>(columns+1):
			columns+=1
		elif rows<(columns-1):
			columns-=1
		else:
			break
	return columns
		
#------------------------------------------------------------------------------
def get_rotation(coords, target_coords):
    delta_x = coords[0] - target_coords[0]
    delta_y = coords[1] - target_coords[1]
    
    # Calculate the angle in radians
    angle_rad = math.atan2(delta_x, delta_y)
    
    # Convert the angle to degrees and ensure it's positive
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
        
    return angle_deg

#------------------------------------------------------------------------------
def get_transfer_results(source_amount, destination_amount, destination_maximum):
	'''get resulting numbers from transfering an amount of something somewhere else'''

	# Calculate the amount that can be transferred without going over the maximum
	transferable_amount = min(source_amount, destination_maximum - destination_amount)

	# Update the source and destination amounts
	source_amount -= transferable_amount
	destination_amount += transferable_amount

	# round 
	source_amount=round(source_amount,2)
	destination_amount=round(destination_amount,2)

	return source_amount, destination_amount


#------------------------------------------------------------------------------
def get_vector_addition(first_vec,second_vec):
	'''add together two vector 2s'''
	result=[first_vec[0]+second_vec[0],first_vec[1]+second_vec[1]]
	return result

#------------------------------------------------------------------------------
def get_vector_length(vec2):
	return math.sqrt(vec2[0]*vec2[0]+vec2[1]*vec2[1])


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

#------------------------------------------------------------------------------
def randomize_position_and_rotation(worldobj,amount=15,):
	''' takes a world object and randomizes the rotation and position'''
	w=worldobj.world_coords
	worldobj.world_coords=[w[0]+float(random.randint(-amount,amount)),w[1]+float(random.randint(-amount,amount))]
	worldobj.rotation_angle=float(random.randint(0,359))
	worldobj.reset_image=True


#------------------------------------------------------------------------------
def regress_to_zero(var=None,time_passed=None,dead_zone=0.05):
	''' regress a variable to zero over time '''
	if var>0:
		var-=1*time_passed
		if var<dead_zone:
			var=0
	elif var<0:
		var+=1*time_passed
		if var>-dead_zone:
			var=0

	# round
	var=round(var,2)

	return var
	
#------------------------------------------------------------------------------
def round_vector_2(vector):
	return [round(vector[0],2),round(vector[1],2)]





