'''
repo : https://github.com/openmarmot/twe

notes : calculate effective armor thickness
follows the formula from engine/penetration_calculator

remember for armor
0 - vertical. no slope. no advantage to effective armor
90 - full slope. (impossible)
the closer to 90 the more effective armor you get as the shell has 
to travel through more armor place to pierce through

'''


import sys
import math 

# Check if correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage: python armor_thickness.py armor_thickness armor_slope")
    sys.exit(1)

# Get the parameters
try:
    armor_thickness = float(sys.argv[1])
    armor_slope = float(sys.argv[2])
except ValueError:
    print('Parameters must be numbers')



effective_thickness = armor_thickness / (math.cos(math.radians(armor_slope))) 

print(f'armor thickness: {armor_thickness}')
print(f'armor slope: {armor_slope}')
print(f'effective armor thickness: {round(effective_thickness,2)}')