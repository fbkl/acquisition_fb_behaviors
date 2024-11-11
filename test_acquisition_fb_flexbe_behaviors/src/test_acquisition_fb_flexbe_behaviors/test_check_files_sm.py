#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from acquisition_fb_flexbe_states.check_if_files_were_saved_state import CheckFileSavedState
from acquisition_fb_flexbe_states.set_as_ros_param import SetRosParamState
from acquisition_fb_flexbe_states.tmux_setup_state import TmuxSetupState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Sat Nov 09 2024
@author: frekle
'''
class test_check_filesSM(Behavior):
	'''
	test checking for files functionality
	'''


	def __init__(self):
		super(test_check_filesSM, self).__init__()
		self.name = 'test_check_files'

		# parameters of this behavior

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		session_name = "testtt"
		# x:900 y:343, x:130 y:464
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.expected_files = ["a.txt"]

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:262 y:21
			OperatableStateMachine.add('set_params_for_test',
										SetRosParamState(namespace_prefix="rqt_acquisition", param_dic={"save_path":"/tmp","activity_name":"wind_surfing"}),
										transitions={'continue': 'Launches_Some_Tester', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Full})

			# x:478 y:356
			OperatableStateMachine.add('are_files_there',
										CheckFileSavedState(filename_param="rqt_acquisition/activity_name", dirname_param="rqt_acquisition/save_path"),
										transitions={'continue': 'finished', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Full},
										remapping={'expected_files': 'expected_files'})

			# x:480 y:150
			OperatableStateMachine.add('Launches_Some_Tester',
										TmuxSetupState(session_name=session_name, startup_dic={"test_pane":["touch /tmp/DATE_TIMEwind_surfing89_a.txt"]}),
										transitions={'continue': 'are_files_there', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Full})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
