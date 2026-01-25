'''
repo : https://github.com/openmarmot/twe

notes : 

testing area for queries 
'''

import sqlite3


# Connect to the SQLite database
conn = sqlite3.connect('data.sqlite')

# Create a cursor object
cursor = conn.cursor()

cursor.execute("SELECT name,projectile_material,case_material,grain_weight,velocity,contact_effect,shrapnel_count FROM projectile_data")

# Fetch all column names
column_names = [description[0] for description in cursor.description]

# Fetch all rows from the table
rows = cursor.fetchall()

# Close the database connection
conn.close()

# Convert rows to dictionary, excluding the 'id' field
data_dict = {}
for row in rows:
    row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
    key = row_dict.pop('name')
    data_dict[key] = row_dict

# Print the resulting dictionary
print(data_dict)
