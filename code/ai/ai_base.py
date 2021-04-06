
'''
module : ai.ai_base.py
version : see module_version variable
Language : Python 3.x
author : andrew christ
email : andrew@openmarmot.com
notes :
'''


#import built in modules

#import custom packages

# module specific variables
module_version='0.0' #module software version
module_last_update_date='July 02 2016' #date of last update

#global variables

class AIBase(object):
	def __init__(self, OWNER):
		self.owner=OWNER #WorldObject that is the parent


	def update(self):
		pass

	def handleEvent(self, EVENT, EVENT_DATA):
		pass
