#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from acquisition_fb_flexbe_behaviors.ar_brio_sm import ar_brioSM
from acquisition_fb_flexbe_behaviors.imu_startup_sequence_sm import imu_startup_sequenceSM
from acquisition_fb_flexbe_states.VENVtmux_setup_from_yaml_state import VENVTmuxSetupFromYamlState
from acquisition_fb_flexbe_states.check_if_alive import HostAliveState
from acquisition_fb_flexbe_states.env_vars_userdata_setter import MomentArmAndLibraryEnvSetterUserDataState
from acquisition_fb_flexbe_states.multi_service_call_state import MultiServiceCallState
from acquisition_fb_flexbe_states.multi_set_some_param_state import MultiSetSomeParamState
from acquisition_fb_flexbe_states.tmux_setup_state import TmuxSetupState
from acquisition_fb_flexbe_states.userdata_from_params_state import UserDataFromParamsState
from acquisition_fb_flexbe_states.variable_multi_service_call_state import VariableMultiServiceCallState
from acquisition_fb_flexbe_states.variable_set_name_and_path_from_param_state import VariableMultiSetNameAndPathFromParamState
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.log_state import LogState
from flexbe_states.operator_decision_state import OperatorDecisionState
from flexbe_states.wait_state import WaitState
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Wed Oct 23 2024
@author: frekle
'''
class Acquire_EverythingSM(Behavior):
	'''
	acquire using embeddable IMU behavior
- with tmux 
- IMUs with upright start
- IK using old heading 
- playing sounds
- now tries to add camera as well
- adds rqt_acquisition
	'''


	def __init__(self):
		super(Acquire_EverythingSM, self).__init__()
		self.name = 'Acquire_Everything'

		# parameters of this behavior
		self.add_parameter('run_insoles', True)
		self.add_parameter('run_id', True)
		self.add_parameter('run_so', False)
		self.add_parameter('run_vicon_controller', True)
		self.add_parameter('remove_path', '/srv/host_data')
		self.add_parameter('append_path', 'd:/ViconData/Ruoli/Motion_Insole')
		self.add_parameter('vicon_ip', '192.168.1.103')
		self.add_parameter('vicon_port', 1030)
		self.add_parameter('session_id', 'SESSION1')
		self.add_parameter('activity_name', 'test')
		self.add_parameter('subject_id', 'SUB01')
		self.add_parameter('weight', 0)
		self.add_parameter('height', 0)
		self.add_parameter('insole_size', 'S6 (42-43)')

		# references to used behaviors
		self.add_behavior(imu_startup_sequenceSM, 'Imu_Startup_Sequence')
		self.add_behavior(ar_brioSM, 'Node_Startup/ar_brio')

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

		# ! 1074 45 
		# TODO:Here we also need to make sure we are loading the correct models every time!

		# O 519 273 /Calibration_and_Heading
		# This published the tfs for showing the IMUs on rViz|n|nNot really necessary, since we are not using this inside the node just yet

		# O 500 109 /Calibration_and_Heading
		# We are using just the pelvis for heading. This is maybe not ideal, since a combined heading of more imus maybe is better



	def create(self):
		save_dir = "/srv/host_data/tmp"
		tmux_yaml_path = "/catkin_ws/src/ros_biomech/acquisition_state_machines/acquisition_of_raw_data/config/"
		imu_list = ["torso","pelvis","femur_r","tibia_r","talus_r","femur_l","tibia_l","talus_l"]
		calib_sound_file = "/srv/host_data/calib.wav"
		ik_yaml = "plus_ik.yaml"
		insole_yaml = "insoles_only.yaml"
		id_yaml = "id_only.yaml"
		so_yaml = "so_only.yaml"
		vicon_yaml = "vicon_only.yaml"
		vicon_vars = {"REMOVE":self.remove_path,"APPEND":self.append_path,"VICON_IP":self.vicon_ip,"VICON_PORT":self.vicon_port}
		tmux_session_name = "testtt"
		model_dir = "/srv/host_data/models/height_adjusted/"
		model_name = f"gait1992_{str(self.height*100)}"
		model_file = f"{model_dir}{model_name}.osim"
		moment_arm_lib = f"{model_dir}libMomentArm_{model_name}.so"
		export_vars = {"MODEL_FILE":model_file,"MOMENT_ARM_LIB":moment_arm_lib,"NUM_PROC_SO":4,"SHOW_VIZ_OTHER":"true"}
		# x:1421 y:812, x:162 y:458
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.activity_save_dir = ""
		_state_machine.userdata.activity_save_name = ""
		_state_machine.userdata.use_insoles = self.run_insoles
		_state_machine.userdata.use_id = self.run_id
		_state_machine.userdata.use_so = self.run_so
		_state_machine.userdata.node_start_list = []
		_state_machine.userdata.use_vicon_controller = self.run_vicon_controller
		_state_machine.userdata.parked_nodes = ["/ik"]

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]

		# x:71 y:247, x:559 y:584
		_sm_recording_trial_0 = OperatableStateMachine(outcomes=['failed', 'done'], input_keys=['node_start_list'])

		with _sm_recording_trial_0:
			# x:483 y:4
			OperatableStateMachine.add('Start_Recording_Srv',
										VariableMultiServiceCallState(predicate="/start_recording", prefix=""),
										transitions={'done': 'Recording', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'node_start_list'})

			# x:524 y:95
			OperatableStateMachine.add('Recording',
										LogState(text="Recording...", severity=Logger.REPORT_HINT),
										transitions={'done': 'Stop_Recording_Srv'},
										autonomy={'done': Autonomy.Full})

			# x:499 y:209
			OperatableStateMachine.add('Stop_Recording_Srv',
										VariableMultiServiceCallState(predicate="/stop_recording", prefix=""),
										transitions={'done': 'Write_Sto_Srv', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'node_start_list'})

			# x:504 y:314
			OperatableStateMachine.add('Write_Sto_Srv',
										VariableMultiServiceCallState(predicate="/write_sto", prefix=""),
										transitions={'done': 'Clear_Loggers', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'node_start_list'})

			# x:510 y:446
			OperatableStateMachine.add('Clear_Loggers',
										VariableMultiServiceCallState(predicate="/clear_loggers", prefix=""),
										transitions={'done': 'done', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'node_start_list'})


		# x:1304 y:830, x:862 y:381
		_sm_acquisition_setup_1 = OperatableStateMachine(outcomes=['finished', 'failed'], output_keys=['export_vars'])

		with _sm_acquisition_setup_1:
			# x:420 y:52
			OperatableStateMachine.add('Set_Model_Path',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="model_path", value_of_param=model_file, check_if_nodes_exist=False),
										transitions={'done': 'Set_Lib_Path', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:422 y:210
			OperatableStateMachine.add('Set_Activity_Name',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="activity_name", value_of_param=self.activity_name, check_if_nodes_exist=False),
										transitions={'done': 'Set_Subject_Id', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:423 y:137
			OperatableStateMachine.add('Set_Lib_Path',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="lib_path", value_of_param=moment_arm_lib, check_if_nodes_exist=False),
										transitions={'done': 'Set_Activity_Name', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:422 y:416
			OperatableStateMachine.add('Set_Save_Path',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="save_path", value_of_param=save_dir, check_if_nodes_exist=False),
										transitions={'done': 'Load_Rqt_Acquisition', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:423 y:347
			OperatableStateMachine.add('Set_Session_Id',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="session_num", value_of_param=self.session_id, check_if_nodes_exist=False),
										transitions={'done': 'Set_Save_Path', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:423 y:279
			OperatableStateMachine.add('Set_Subject_Id',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="subject_id", value_of_param=self.subject_id, check_if_nodes_exist=False),
										transitions={'done': 'Set_Session_Id', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:430 y:810
			OperatableStateMachine.add('Setter',
										MomentArmAndLibraryEnvSetterUserDataState(),
										transitions={'done': 'call_disable_setting_model_in_acquision'},
										autonomy={'done': Autonomy.Off},
										remapping={'model': 'model_path', 'lib': 'lib_path', 'env_vars': 'export_vars'})

			# x:417 y:714
			OperatableStateMachine.add('Update_Lib',
										UserDataFromParamsState(param_path="rqt_acquisition/lib_path", data_property_name="lib_path"),
										transitions={'done': 'Setter'},
										autonomy={'done': Autonomy.Off},
										remapping={'lib_path': 'lib_path'})

			# x:446 y:606
			OperatableStateMachine.add('Update_Model',
										UserDataFromParamsState(param_path="rqt_acquisition/model_path", data_property_name="model_path"),
										transitions={'done': 'Update_Lib'},
										autonomy={'done': Autonomy.Off},
										remapping={'model_path': 'model_path'})

			# x:758 y:811
			OperatableStateMachine.add('call_disable_setting_model_in_acquision',
										MultiServiceCallState(multi_service_list="/rqt_acquisition/set_running", predicate="", prefix=""),
										transitions={'done': 'finished', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:424 y:493
			OperatableStateMachine.add('Load_Rqt_Acquisition',
										TmuxSetupState(session_name=tmux_session_name, startup_dic={"acq":["rqt --standalone rqt_acquisition"]}),
										transitions={'continue': 'Update_Model', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Full, 'failed': Autonomy.Off})


		# x:953 y:222, x:68 y:409
		_sm_node_startup_2 = OperatableStateMachine(outcomes=['failed', 'ok'], input_keys=['use_id', 'use_insoles', 'use_so', 'node_start_list', 'use_vicon_controller'], output_keys=['node_start_list'])

		with _sm_node_startup_2:
			# x:68 y:66
			OperatableStateMachine.add('Acquisition_Setup',
										_sm_acquisition_setup_1,
										transitions={'finished': 'ar_brio', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'export_vars': 'export_vars'})

			# x:479 y:446
			OperatableStateMachine.add('Load_ID_Nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+id_yaml, append_node=["/id_node"]),
										transitions={'continue': 'Run_SO', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'load_env': 'export_vars'})

			# x:488 y:203
			OperatableStateMachine.add('Load_IK_nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+ik_yaml, append_node=["/ik"]),
										transitions={'continue': 'Run_Insole', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'load_env': 'export_vars'})

			# x:476 y:274
			OperatableStateMachine.add('Load_Insole_Nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+insole_yaml, append_node=["/moticon_insoles"]),
										transitions={'continue': 'Turn_On_Insoles', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'load_env': 'export_vars'})

			# x:472 y:542
			OperatableStateMachine.add('Load_SO_Nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+so_yaml, append_node=["/so_node"]),
										transitions={'continue': 'ok', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'load_env': 'export_vars'})

			# x:481 y:125
			OperatableStateMachine.add('Load_Vicon_Controller_Node',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+vicon_yaml, append_node=["/vicon_control"]),
										transitions={'continue': 'Load_IK_nodes', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'load_env': 'export_vars'})

			# x:286 y:340
			OperatableStateMachine.add('Run_ID',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_ID_Nodes', 'false': 'ok'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_id'})

			# x:293 y:262
			OperatableStateMachine.add('Run_Insole',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Insole_Nodes', 'false': 'ok'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_insoles'})

			# x:286 y:421
			OperatableStateMachine.add('Run_SO',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_SO_Nodes', 'false': 'ok'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_so'})

			# x:266 y:152
			OperatableStateMachine.add('Run_Vicon_Controller',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Vicon_Controller_Node', 'false': 'Load_IK_nodes'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_vicon_controller'})

			# x:515 y:362
			OperatableStateMachine.add('Turn_On_Insoles',
										LogState(text="Turn on Tablet and insoles and put shoes on", severity=Logger.REPORT_HINT),
										transitions={'done': 'Run_ID'},
										autonomy={'done': Autonomy.Full})

			# x:295 y:26
			OperatableStateMachine.add('ar_brio',
										self.use_behavior(ar_brioSM, 'Node_Startup/ar_brio'),
										transitions={'finished': 'Run_Vicon_Controller', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit})


		# x:264 y:58, x:130 y:432
		_sm_check_if_devices_are_on_3 = OperatableStateMachine(outcomes=['done', 'fail'])

		with _sm_check_if_devices_are_on_3:
			# x:50 y:42
			OperatableStateMachine.add('is_router_on',
										HostAliveState(hostname="192.168.1.1", waittime=20),
										transitions={'continue': 'done', 'failed': 'turn_on_router'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:50 y:179
			OperatableStateMachine.add('turn_on_router',
										LogState(text="turn on router!!", severity=Logger.REPORT_ERROR),
										transitions={'done': 'fail'},
										autonomy={'done': Autonomy.Off})



		with _state_machine:
			# x:334 y:58
			OperatableStateMachine.add('Node_Startup',
										_sm_node_startup_2,
										transitions={'failed': 'failed', 'ok': 'Check_If_Devices_Are_On'},
										autonomy={'failed': Autonomy.Inherit, 'ok': Autonomy.Inherit},
										remapping={'use_id': 'use_id', 'use_insoles': 'use_insoles', 'use_so': 'use_so', 'node_start_list': 'node_start_list', 'use_vicon_controller': 'use_vicon_controller'})

			# x:650 y:17
			OperatableStateMachine.add('Check_If_Devices_Are_On',
										_sm_check_if_devices_are_on_3,
										transitions={'done': 'Imu_Startup_Sequence', 'fail': 'failed'},
										autonomy={'done': Autonomy.Inherit, 'fail': Autonomy.Inherit})

			# x:650 y:161
			OperatableStateMachine.add('Imu_Startup_Sequence',
										self.use_behavior(imu_startup_sequenceSM, 'Imu_Startup_Sequence',
											default_keys=['imu_export_vars']),
										transitions={'finished': 'Start_Parked_Nodes', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'imu_list': 'imu_list'})

			# x:1093 y:625
			OperatableStateMachine.add('Record_Another',
										OperatorDecisionState(outcomes=["yes", "no"], hint=None, suggestion=None),
										transitions={'yes': 'Calibrate_IK', 'no': 'finished'},
										autonomy={'yes': Autonomy.Off, 'no': Autonomy.Off})

			# x:650 y:798
			OperatableStateMachine.add('Recording_trial',
										_sm_recording_trial_0,
										transitions={'failed': 'failed', 'done': 'Record_Another'},
										autonomy={'failed': Autonomy.Inherit, 'done': Autonomy.Inherit},
										remapping={'node_start_list': 'node_start_list'})

			# x:595 y:623
			OperatableStateMachine.add('Sets_Filename_And_Path_From_Rqt_Acquistion_Params',
										VariableMultiSetNameAndPathFromParamState(prefix="", suffix="/set_name_and_path", filename_param="rqt_acquisition/activity_name", dirname_param="rqt_acquisition/save_path"),
										transitions={'done': 'Start_Recording_Question_Mark', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'node_start_list'})

			# x:658 y:276
			OperatableStateMachine.add('Start_Parked_Nodes',
										VariableMultiServiceCallState(predicate="/start_now", prefix=""),
										transitions={'done': 'Wait_For_Nodes_To_Be_Ready', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'parked_nodes'})

			# x:650 y:720
			OperatableStateMachine.add('Start_Recording_Question_Mark',
										LogState(text="Is the calibration and the heading OK?\n Proceeding will start recording the trial", severity=Logger.REPORT_HINT),
										transitions={'done': 'Recording_trial'},
										autonomy={'done': Autonomy.Full})

			# x:650 y:387
			OperatableStateMachine.add('Wait_For_Nodes_To_Be_Ready',
										WaitState(wait_time=5),
										transitions={'done': 'Calibrate_IK'},
										autonomy={'done': Autonomy.Full})

			# x:650 y:538
			OperatableStateMachine.add('Calibrate_IK',
										MultiServiceCallState(multi_service_list="/ik", predicate="/calibrate", prefix=""),
										transitions={'done': 'Sets_Filename_And_Path_From_Rqt_Acquistion_Params', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
