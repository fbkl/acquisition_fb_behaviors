#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from acquisition_fb_flexbe_states.userdata_from_params_state import UserDataFromParamsState
from flexbe_states.log_key_state import LogKeyState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Wed Oct 23 2024
@author: bfk
'''
class test_set_user_data_from_paramsSM(Behavior):
	'''
	test of set_user_data_from_params state
	'''


	def __init__(self):
		super(test_set_user_data_from_paramsSM, self).__init__()
		self.name = 'test_set_user_data_from_params'

		# parameters of this behavior

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:30 y:477, x:130 y:477
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.my_userdata_thing = {}

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:215 y:121
			OperatableStateMachine.add('aa',
										UserDataFromParamsState(param_path="test", data_property_name="my_userdata_thing"),
										transitions={'done': 'ddddd'},
										autonomy={'done': Autonomy.Off},
										remapping={'my_userdata_thing': 'my_userdata_thing'})

			# x:500 y:141
			OperatableStateMachine.add('ddddd',
										LogKeyState(text="dddd {}", severity=Logger.REPORT_HINT),
										transitions={'done': 'finished'},
										autonomy={'done': Autonomy.Off},
										remapping={'data': 'my_userdata_thing'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
