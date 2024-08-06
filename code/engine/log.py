'''
module : log.py
language : Python 3.x
email : andrew@openmarmot.com
notes : 

error/misc logging
'''


data_log=[]



#---------------------------------------------------------------------------
def add_data(classification,data,print):
    # classification : error/warn/info
    # data : text log data
    # print: True/False - whether to print it
    global data_log
    message=classification+' : '+data
    data_log.append(message)
    if print:
        print(message)