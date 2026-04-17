#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from acquisition_fb_flexbe_states.variable_tmux_setup_from_yaml_state import VariableTmuxSetupFromYamlState
from flexbe_states.log_state import LogState
from flexbe_states.wait_state import WaitState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Thu Mar 19 2026
@author: fbk
'''
class bringup_vioSM(Behavior):
	'''
	trying to get vio running remotely,,
	'''


	def __init__(self):
		super(bringup_vioSM, self).__init__()
		self.name = 'bringup_vio'

		# parameters of this behavior
		self.add_parameter('vio_yaml_file', '')

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:

		# ! 41 513 
		# !!!! here we need to also clear all the started nodes so we are back in the beginning, |n|nwe can kill nodes by name with rosnode kill |n|nand we can do a cleanup with they are dangling with rosnode cleanuo

		# ! 657 14 /Recording_trial
		# Missing sending the start time to everyone so that we have a very similar setup to the playback

		# O 265 11 /Calibration_and_Heading
		# Right now we are not using these results to calibrate the IK node just yet. |n|nThe only guys that use this are the resolve headings service to show the imus and the external heading calibrator which uses the pelvis avg quaternion

		# O 335 93 /Check_If_Devices_Are_On
		# TODO: This should be a part of the device monitoring bit, so don't have to run this as a state and also since they may fail at any point

		# O 519 273 /Calibration_and_Heading
		# This published the tfs for showing the IMUs on rViz|n|nNot really necessary, since we are not using this inside the node just yet

		# O 500 109 /Calibration_and_Heading
		# We are using just the pelvis for heading. This is maybe not ideal, since a combined heading of more imus maybe is better



	def create(self):
		tmux_yaml_path = "/catkin_ws/src/ros_biomech/acquisition_state_machines/acquisition_of_raw_data/config/"
		use_session = "testtt"
		# x:961 y:87, x:216 y:388
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'], input_keys=['vio_export_vars'], output_keys=['vio_export_vars'])
		_state_machine.userdata.vio_export_vars = {}
		_state_machine.userdata.disregard = []

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:133 y:64
			OperatableStateMachine.add('Load_VIO_Nodes',
										VariableTmuxSetupFromYamlState(session_name=use_session, startup_yaml=tmux_yaml_path+self.vio_yaml_file, append_node=[]),
										transitions={'continue': 'Wait_for_VIO_Start', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'disregard', 'load_env': 'vio_export_vars'})

			# x:344 y:161
			OperatableStateMachine.add('Wait_for_VIO_Start',
										WaitState(wait_time=3),
										transitions={'done': 'don_cameras'},
										autonomy={'done': Autonomy.Off})

			# x:723 y:79
			OperatableStateMachine.add('don_cameras',
										LogState(text="place CAMERAs", severity=Logger.REPORT_HINT),
										transitions={'done': 'finished'},
										autonomy={'done': Autonomy.Full})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
