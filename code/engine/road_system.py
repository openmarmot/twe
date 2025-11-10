'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : road_system is a point to point road composed of road_segments
'''

# import custom packages
import engine.math_2d
import math

class RoadSystem():

    def __init__(self):

        # segments
        # type - string name that represents what type of road segment it is
        #[[world_coords,rotation,type]]
        self.segments = []

        # segment types
        #[[type_name,type_height]]
        self.segment_types = []
        self.segment_types.append(['road_300', 300])


    def create(self,start_coords,end_coords):
        # start_coords,end_coords [0.0,0.0]
        # rotation is in degrees
        actual_rotation=engine.math_2d.get_rotation(start_coords,end_coords)
        actual_distance=engine.math_2d.get_distance(start_coords,end_coords)

        # for now calculated_rotation is the closest angle of 0,90,180,270
        calculated_rotation = round(actual_rotation / 90) * 90 % 360

        # determine the number of segments needed and the overlap
        # overlap defaults to the segment type_height
        # if there is a remainder we will go one over and slightly overlap them
        segment_height = self.segment_types[0][1]
        number_of_segments = math.ceil(actual_distance / segment_height)

        # fill out the segments array
        dir = engine.math_2d.get_heading_vector(start_coords, end_coords)
        for i in range(number_of_segments):
            center_pos = [start_coords[0] + (i * segment_height + segment_height / 2) * dir[0], 
                          start_coords[1] + (i * segment_height + segment_height / 2) * dir[1]]
            self.segments.append([center_pos, actual_rotation, 'road_300'])
