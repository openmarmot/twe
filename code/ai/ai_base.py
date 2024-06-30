
'''
module : ai.ai_base.py
language : Python 3.x
email : andrew@openmarmot.com
notes :
'''

#import built in modules

#import custom packages

#global variables

class AIBase(object):
	def __init__(self, OWNER):
		self.owner=OWNER #WorldObject that is the parent

	def update(self):
		pass

	def handle_event(self, event, event_data):
		# EVENT - text describing event
        # EVENT_DATA - most likely a world_object but could be anything
		pass
