'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : 

error/misc logging
'''

from datetime import datetime
import csv
import os
data_log=[]

# dictionaries are appended to this by ai_human upon death
human_death_log=[]



#---------------------------------------------------------------------------
def add_data(classification,data,print_message):
    '''add log data'''
    # classification : error/warn/info
    # data : text log data
    # print: True/False - whether to print it
    global data_log
    message=classification+' : '+data
    data_log.append({
        'classification':classification,
        'data':data
    })

    if print_message:
        print(message)

#---------------------------------------------------------------------------
def export_to_csv(dict_list,filename_prefix):
    '''export to csv'''
    output_dir='logs'
    # Get current date and time for filename
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    filename = f"{filename_prefix}_{current_time}.csv"
    
    # Check if list is empty
    if not dict_list:
        print("Empty dictionary list provided")
        return
    
    # Get column names from first dictionary
    fieldnames = dict_list[0].keys()

    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)
    
    # Write to CSV file
    with open(full_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write all rows
        writer.writerows(dict_list)
    
    print(f"CSV file saved as: {filename}")
    return filename

#---------------------------------------------------------------------------
def export_all():
    '''export all data'''
    export_to_csv(data_log,'game_log')
    export_to_csv(human_death_log,'death_log')