'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : 

error/misc logging
'''


data_log=[]



#---------------------------------------------------------------------------
def add_data(classification,data,print_message):
    # classification : error/warn/info
    # data : text log data
    # print: True/False - whether to print it
    global data_log
    message=classification+' : '+data
    data_log.append(message)
    if print_message:
        print(message)