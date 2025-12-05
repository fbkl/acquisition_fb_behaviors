#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from acquisition_fb_flexbe_states.multi_service_userdata_call_state import MultiServiceUserdataCallState
from acquisition_fb_flexbe_states.variable_tmux_setup_from_yaml_state import VariableTmuxSetupFromYamlState
from acquisition_fb_flexbe_states.wait_for_diags_userdata import WaitForDiagsUserdata
from flexbe_states.log_state import LogState
from flexbe_states.wait_state import WaitState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Mon Apr 22 2024
@author: frekle
'''
class imu_startup_sequenceSM(Behavior):
	'''
	embeddable imu start behavior
	'''


	def __init__(self):
		super(imu_startup_sequenceSM, self).__init__()
		self.name = 'imu_startup_sequence'

		# parameters of this behavior
		self.add_parameter('dummy_imus', False)
		self.add_parameter('wait_to_start', True)
		self.add_parameter('imu_yaml_file', 'imus2392.yaml')

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
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'], input_keys=['imu_export_vars', 'imu_list'], output_keys=['imu_list'])
		_state_machine.userdata.imu_list = ["torso","pelvis","femur_r","tibia_r","talus_r","femur_l","tibia_l","talus_l"]
		_state_machine.userdata.disregard = []
		_state_machine.userdata.imu_export_vars = {"DUMMY_IMUS":self.dummy_imus,"WAIT_TO_START":self.wait_to_start}

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]

		# x:949 y:156, x:130 y:477
		_sm_turn_on_imus_0 = OperatableStateMachine(outcomes=['done', 'failed'], input_keys=['imu_list'])

		with _sm_turn_on_imus_0:
			# x:30 y:47
			OperatableStateMachine.add('turn_on_imus',
										LogState(text="Turn on imus in a line", severity=Logger.REPORT_HINT),
										transitions={'done': 'start_imus2'},
										autonomy={'done': Autonomy.Full})

			# x:207 y:58
			OperatableStateMachine.add('start_imus2',
										MultiServiceUserdataCallState(predicate="/start_now", prefix="/ximu_", wait_to_start=True, timeout=60),
										transitions={'done': 'wait_for_things_to_be_done', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'imu_list'})

			# x:438 y:58
			OperatableStateMachine.add('wait_for_things_to_be_done',
										WaitState(wait_time=1),
										transitions={'done': 'imu_diags2'},
										autonomy={'done': Autonomy.Off})

			# x:409 y:278
			OperatableStateMachine.add('imu_diags2',
										WaitForDiagsUserdata(timeout=100),
										transitions={'continue': 'done', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'diags_list': 'imu_list'})



		with _state_machine:
			# x:133 y:64
			OperatableStateMachine.add('Load_IMU_Nodes',
										VariableTmuxSetupFromYamlState(session_name=use_session, startup_yaml=tmux_yaml_path+self.imu_yaml_file, append_node=[]),
										transitions={'continue': 'Wait_for_Imu_Start_Services', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'disregard', 'load_env': 'imu_export_vars'})

			# x:492 y:314
			OperatableStateMachine.add('Turn_On_IMUs',
										_sm_turn_on_imus_0,
										transitions={'done': 'don_imus', 'failed': 'failed'},
										autonomy={'done': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'imu_list': 'imu_list'})

			# x:344 y:161
			OperatableStateMachine.add('Wait_for_Imu_Start_Services',
										WaitState(wait_time=3),
										transitions={'done': 'Turn_On_IMUs'},
										autonomy={'done': Autonomy.Off})

			# x:723 y:79
			OperatableStateMachine.add('don_imus',
										LogState(text="place IMUs", severity=Logger.REPORT_HINT),
										transitions={'done': 'finished'},
										autonomy={'done': Autonomy.Full})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
