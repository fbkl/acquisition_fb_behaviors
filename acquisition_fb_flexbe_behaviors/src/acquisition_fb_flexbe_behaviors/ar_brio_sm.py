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
from flexbe_states.check_condition_state import CheckConditionState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Wed Oct 09 2024
@author: frekle
'''
class ar_brioSM(Behavior):
	'''
	tries to load the brio camera with the proper map orientations, the marker finder thing and the rviz visuals
	'''


	def __init__(self):
		super(ar_brioSM, self).__init__()
		self.name = 'ar_brio'

		# parameters of this behavior
		self.add_parameter('camera_dev_num', 4)
		self.add_parameter('load_ar_nodes', True)

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		session_name = "testtt"
		start_up_yaml = "ar.yaml"
		yaml_config_dir = "/catkin_ws/src/ros_biomech/acquisition_state_machines/acquisition_of_raw_data/config/"
		# x:30 y:365, x:200 y:456
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'], output_keys=['should_load_ar'])
		_state_machine.userdata.node_start_list = []
		_state_machine.userdata.load_env = {"CAM_DEV":str(self.camera_dev_num)}
		_state_machine.userdata.should_load_ar = self.load_ar_nodes

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:145 y:132
			OperatableStateMachine.add('Shoul_Load_Ar',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Ar_Nodes', 'false': 'finished'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'should_load_ar'})

			# x:470 y:104
			OperatableStateMachine.add('Load_Ar_Nodes',
										VariableTmuxSetupFromYamlState(session_name=session_name, startup_yaml=yaml_config_dir+start_up_yaml, append_node=[]),
										transitions={'continue': 'finished', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Inherit, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'load_env': 'load_env'})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
