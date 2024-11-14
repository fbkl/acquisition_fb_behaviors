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
from acquisition_fb_flexbe_states.check_if_files_were_saved_state import CheckFileSavedState
from acquisition_fb_flexbe_states.env_vars_userdata_setter import MomentArmAndLibraryEnvSetterUserDataState
from acquisition_fb_flexbe_states.moticon_insole_vars_userdata_setter import MoticonInsoleSetterUserDataState
from acquisition_fb_flexbe_states.multi_service_call_state import MultiServiceCallState
from acquisition_fb_flexbe_states.multi_set_some_param_state import MultiSetSomeParamState
from acquisition_fb_flexbe_states.play_sound_state import PlaySoundState
from acquisition_fb_flexbe_states.set_as_ros_param import SetRosParamState
from acquisition_fb_flexbe_states.tmux_setup_state import TmuxSetupState
from acquisition_fb_flexbe_states.userdata_from_params_state import UserDataFromParamsState
from acquisition_fb_flexbe_states.variable_multi_service_call_state import VariableMultiServiceCallState
from acquisition_fb_flexbe_states.variable_set_name_and_path_from_param_state import VariableMultiSetNameAndPathFromParamState
from acquisition_fb_flexbe_states.wait_for_messages import WaitForMessages
from flexbe_states.check_condition_state import CheckConditionState
from flexbe_states.log_state import LogState
from flexbe_states.operator_decision_state import OperatorDecisionState
from gait1992_fb_flexbe_behaviors.urdf_simple_scaling_sm import urdf_simple_scalingSM
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]
import rospkg

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
		self.add_parameter('run_so', True)
		self.add_parameter('run_vicon_controller', True)
		self.add_parameter('remove_path', '/srv/host_data')
		self.add_parameter('append_path', 'd:/ViconData')
		self.add_parameter('vicon_ip', '192.168.1.103')
		self.add_parameter('vicon_port', 1030)
		self.add_parameter('session_id', 'SESSION0')
		self.add_parameter('activity_name', 'test1')
		self.add_parameter('subject_id', 'SUB0')
		self.add_parameter('weight', 75)
		self.add_parameter('height', 1.75)
		self.add_parameter('insole_size', 'S6 (42-43)')
		self.add_parameter('combined_acquisition', True)
		self.add_parameter('use_ar_markers_in_ik', False)
		self.add_parameter('show_viz_extensive', False)
		self.add_parameter('record_rosbag', False)
		self.add_parameter('dummy_insoles', True)

		# references to used behaviors
		self.add_behavior(imu_startup_sequenceSM, 'Imu_Startup_Sequence')
		self.add_behavior(ar_brioSM, 'Node_Startup/ar_brio')
		self.add_behavior(urdf_simple_scalingSM, 'Node_Startup/urdf_simple_scaling')

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		self.rospack = rospkg.RosPack()
		# [/MANUAL_INIT]

		# Behavior comments:

		# ! 45 843 
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
		tmux_yaml_path = self.find_pkg("acquisition_of_raw_data")+"/config/"
		imu_list = ["torso","pelvis","femur_r","tibia_r","talus_r","femur_l","tibia_l","talus_l"]
		calib_sound_file = "/srv/host_data/calib.wav"
		ik_yaml = "plus_ik.yaml"
		insole_yaml = "dummy_insoles.yaml" if self.dummy_insoles else "insoles_only.yaml"
		id_yaml = "id_only.yaml"
		so_yaml = "so_only.yaml"
		vicon_yaml = "vicon_only.yaml"
		vicon_vars = {"REMOVE":self.remove_path,"APPEND":self.append_path,"VICON_IP":self.vicon_ip,"VICON_PORT":self.vicon_port}
		tmux_session_name = "testtt"
		model_dir = "/srv/host_data/models/height_adjusted/"
		model_name = f"gait1992_{str(int(self.height*100))}"
		model_file = f"{model_dir}{model_name}.osim"
		moment_arm_lib = f"{model_dir}libMomentArm_{model_name}"
		export_vars = {"MODEL_FILE":model_file,"MOMENT_ARM_LIB":moment_arm_lib,"NUM_PROC_SO":4,"USE_AR":self.use_ar_markers_in_ik,"COMBINED_ACQUISITION":self.combined_acquisition}
		combined_perspective_file = self.find_pkg("rqt_acquisition")+"/Control_Acquisition_small_tabs.perspective"
		common_vars = {"SHOW_VIZ_OTHER":self.show_viz_extensive,}
		# x:1420 y:614, x:289 y:786
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.activity_save_dir = ""
		_state_machine.userdata.activity_save_name = ""
		_state_machine.userdata.use_insoles = self.run_insoles
		_state_machine.userdata.use_id = self.run_id
		_state_machine.userdata.use_so = self.run_so
		_state_machine.userdata.node_start_list = []
		_state_machine.userdata.use_vicon_controller = self.run_vicon_controller
		_state_machine.userdata.parked_nodes = ["/ik"]
		_state_machine.userdata.export_vars = export_vars
		_state_machine.userdata.should_load_ar = self.use_ar_markers_in_ik
		_state_machine.userdata.use_combined_acquisition = self.combined_acquisition
		_state_machine.userdata.vicon_vars = vicon_vars
		_state_machine.userdata.insole_vars = {}
		_state_machine.userdata.insole_model = self.insole_size
		_state_machine.userdata.common_vars = common_vars
		_state_machine.userdata.save_file_list = []

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]

		# x:71 y:247, x:585 y:783
		_sm_recording_trial_0 = OperatableStateMachine(outcomes=['failed', 'done'], input_keys=['node_start_list', 'save_file_list'])

		with _sm_recording_trial_0:
			# x:483 y:4
			OperatableStateMachine.add('Start_Recording_Srv',
										VariableMultiServiceCallState(predicate="/start_recording", prefix=""),
										transitions={'done': 'Recording', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'node_start_list'})

			# x:510 y:446
			OperatableStateMachine.add('Clear_Loggers',
										VariableMultiServiceCallState(predicate="/clear_loggers", prefix=""),
										transitions={'done': 'Are_All_The_Files_There', 'failed': 'failed'},
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

			# x:523 y:600
			OperatableStateMachine.add('Are_All_The_Files_There',
										CheckFileSavedState(filename_param="rqt_acquisition/activity_name", dirname_param="rqt_acquisition/save_path", target_time=5),
										transitions={'continue': 'done', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'expected_files': 'save_file_list'})


		# x:1304 y:830, x:862 y:381
		_sm_acquisition_setup_1 = OperatableStateMachine(outcomes=['finished', 'failed'], input_keys=['export_vars', 'should_load_ar', 'use_combined_acquisition', 'common_vars'], output_keys=['export_vars'])

		with _sm_acquisition_setup_1:
			# x:420 y:52
			OperatableStateMachine.add('Set_Model_Path',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="model_path", value_of_param=model_file, check_if_nodes_exist=False),
										transitions={'done': 'Set_Lib_Path', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:108 y:616
			OperatableStateMachine.add('Load_Combined_Perspective',
										TmuxSetupState(session_name=tmux_session_name, startup_dic={"acq":[f"rqt --perspective-file {combined_perspective_file}"]}),
										transitions={'continue': 'Update_Model', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Full, 'failed': Autonomy.Full})

			# x:454 y:640
			OperatableStateMachine.add('Load_Rqt_Acquisition',
										TmuxSetupState(session_name=tmux_session_name, startup_dic={"acq":["rqt --standalone rqt_acquisition"]}),
										transitions={'continue': 'Update_Model', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Full, 'failed': Autonomy.Full})

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
										transitions={'done': 'Combined_Acquistion_Perspective', 'failed': 'failed'},
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

			# x:430 y:869
			OperatableStateMachine.add('Setter',
										MomentArmAndLibraryEnvSetterUserDataState(),
										transitions={'done': 'call_disable_setting_model_in_acquision'},
										autonomy={'done': Autonomy.Off},
										remapping={'model': 'model_path', 'lib': 'lib_path', 'should_load_ar': 'should_load_ar', 'env_vars': 'export_vars', 'common_vars': 'common_vars'})

			# x:448 y:792
			OperatableStateMachine.add('Update_Lib',
										UserDataFromParamsState(param_path="rqt_acquisition/lib_path", data_property_name="lib_path"),
										transitions={'done': 'Setter'},
										autonomy={'done': Autonomy.Off},
										remapping={'lib_path': 'lib_path'})

			# x:448 y:717
			OperatableStateMachine.add('Update_Model',
										UserDataFromParamsState(param_path="rqt_acquisition/model_path", data_property_name="model_path"),
										transitions={'done': 'Update_Lib'},
										autonomy={'done': Autonomy.Off},
										remapping={'model_path': 'model_path'})

			# x:758 y:811
			OperatableStateMachine.add('call_disable_setting_model_in_acquision',
										MultiServiceCallState(multi_service_list="/rqt_acquisition/set_running", predicate="", prefix="", wait_to_start=False, timeout=60),
										transitions={'done': 'finished', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:124 y:459
			OperatableStateMachine.add('Combined_Acquistion_Perspective',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Combined_Perspective', 'false': 'Load_Rqt_Acquisition'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_combined_acquisition'})


		# x:953 y:222, x:68 y:409
		_sm_node_startup_2 = OperatableStateMachine(outcomes=['failed', 'ok'], input_keys=['use_id', 'use_insoles', 'use_so', 'node_start_list', 'use_vicon_controller', 'export_vars', 'should_load_ar', 'use_combined_acquisition', 'vicon_vars', 'insole_model', 'insole_vars', 'common_vars', 'save_file_list'], output_keys=['node_start_list', 'insole_vars', 'save_file_list'])

		with _sm_node_startup_2:
			# x:35 y:174
			OperatableStateMachine.add('Set_Moticon_Insole_Size',
										MoticonInsoleSetterUserDataState(),
										transitions={'done': 'ar_brio'},
										autonomy={'done': Autonomy.Off},
										remapping={'insole_model': 'insole_model', 'insole_vars': 'insole_vars', 'common_vars': 'common_vars', 'insole_length': 'insole_length'})

			# x:479 y:621
			OperatableStateMachine.add('Load_ID_Nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+id_yaml, append_node=["/id_node"], append_save_files=["tau.sto","ik.sto"]),
										transitions={'continue': 'Run_SO', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'export_vars'})

			# x:487 y:286
			OperatableStateMachine.add('Load_IK_nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+ik_yaml, append_node=["/ik"], append_save_files=["_ik_lower"]),
										transitions={'continue': 'Run_Insole', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'export_vars'})

			# x:478 y:349
			OperatableStateMachine.add('Load_Insole_Nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+insole_yaml, append_node=["/moticon_insoles"], append_save_files=["_insole.txt"]),
										transitions={'continue': 'Turn_On_Insoles', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'insole_vars'})

			# x:359 y:725
			OperatableStateMachine.add('Load_SO_Nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+so_yaml, append_node=["/so_visualization"], append_save_files=["so.sto"]),
										transitions={'continue': 'ok', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'export_vars'})

			# x:481 y:125
			OperatableStateMachine.add('Load_Vicon_Controller_Node',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+vicon_yaml, append_node=["/vicon_control"], append_save_files=[]),
										transitions={'continue': 'urdf_simple_scaling', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'vicon_vars'})

			# x:284 y:519
			OperatableStateMachine.add('Run_ID',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_ID_Nodes', 'false': 'ok'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_id'})

			# x:286 y:347
			OperatableStateMachine.add('Run_Insole',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Insole_Nodes', 'false': 'ok'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_insoles'})

			# x:286 y:608
			OperatableStateMachine.add('Run_SO',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_SO_Nodes', 'false': 'ok'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_so'})

			# x:266 y:152
			OperatableStateMachine.add('Run_Vicon_Controller',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Vicon_Controller_Node', 'false': 'urdf_simple_scaling'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_vicon_controller'})

			# x:518 y:433
			OperatableStateMachine.add('Turn_On_Insoles',
										LogState(text="Turn on Tablet and insoles and put shoes on", severity=Logger.REPORT_HINT),
										transitions={'done': 'Turn_On_Insoles_Now'},
										autonomy={'done': Autonomy.Full})

			# x:503 y:535
			OperatableStateMachine.add('Turn_On_Insoles_Now',
										WaitForMessages(topics_list=["/left/insole","/right/insole"], custom_message="Please start acquiring insoles now.", timeout=40),
										transitions={'continue': 'Run_ID', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:177 y:32
			OperatableStateMachine.add('ar_brio',
										self.use_behavior(ar_brioSM, 'Node_Startup/ar_brio',
											parameters={'load_ar_nodes': self.use_ar_markers_in_ik}),
										transitions={'finished': 'Acquisition_Setup', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'should_load_ar': 'should_load_ar'})

			# x:516 y:201
			OperatableStateMachine.add('urdf_simple_scaling',
										self.use_behavior(urdf_simple_scalingSM, 'Node_Startup/urdf_simple_scaling',
											parameters={'model_flexbe_package': "gait1992_fb_flexbe_behaviors", 'height': self.height, 'tf_prefix': "ik", 'ignore_insole_imu_for_vis': True, 'use_gui': False, 'adjustable_tfs': False, 'insole_length': 0.000}),
										transitions={'finished': 'Load_IK_nodes', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'insole_length': 'insole_length'})

			# x:530 y:23
			OperatableStateMachine.add('Acquisition_Setup',
										_sm_acquisition_setup_1,
										transitions={'finished': 'Run_Vicon_Controller', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'export_vars': 'export_vars', 'should_load_ar': 'should_load_ar', 'use_combined_acquisition': 'use_combined_acquisition', 'common_vars': 'common_vars'})



		with _state_machine:
			# x:85 y:37
			OperatableStateMachine.add('Set_Param_Weight',
										SetRosParamState(namespace_prefix="/rqt_acquisition", param_dic={"weight":self.weight}),
										transitions={'continue': 'Node_Startup', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Full})

			# x:844 y:453
			OperatableStateMachine.add('Calibration_Complete',
										PlaySoundState(sound_file="/srv/host_data/calib_complete.wav", retries=5, which_player="paplay"),
										transitions={'continue': 'Say_To_Change_Name', 'failed': 'Say_To_Change_Name'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:679 y:293
			OperatableStateMachine.add('Get_Ready_For_Calibration',
										PlaySoundState(sound_file="/srv/host_data/calib.wav", retries=5, which_player="paplay"),
										transitions={'continue': 'Calibrate_IK', 'failed': 'Calibrate_IK'},
										autonomy={'continue': Autonomy.Full, 'failed': Autonomy.Full})

			# x:657 y:24
			OperatableStateMachine.add('Imu_Startup_Sequence',
										self.use_behavior(imu_startup_sequenceSM, 'Imu_Startup_Sequence',
											default_keys=['imu_export_vars']),
										transitions={'finished': 'Start_Parked_Nodes', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'imu_list': 'imu_list'})

			# x:371 y:31
			OperatableStateMachine.add('Node_Startup',
										_sm_node_startup_2,
										transitions={'failed': 'failed', 'ok': 'Imu_Startup_Sequence'},
										autonomy={'failed': Autonomy.Inherit, 'ok': Autonomy.Inherit},
										remapping={'use_id': 'use_id', 'use_insoles': 'use_insoles', 'use_so': 'use_so', 'node_start_list': 'node_start_list', 'use_vicon_controller': 'use_vicon_controller', 'export_vars': 'export_vars', 'should_load_ar': 'should_load_ar', 'use_combined_acquisition': 'use_combined_acquisition', 'vicon_vars': 'vicon_vars', 'insole_model': 'insole_model', 'insole_vars': 'insole_vars', 'common_vars': 'common_vars', 'save_file_list': 'save_file_list'})

			# x:1210 y:601
			OperatableStateMachine.add('Record_Another',
										OperatorDecisionState(outcomes=["yes", "no"], hint=None, suggestion=None),
										transitions={'yes': 'Get_Ready_For_Calibration', 'no': 'finished'},
										autonomy={'yes': Autonomy.Off, 'no': Autonomy.Off})

			# x:748 y:718
			OperatableStateMachine.add('Recording_trial',
										_sm_recording_trial_0,
										transitions={'failed': 'Trial_Failed', 'done': 'Trial_Finished'},
										autonomy={'failed': Autonomy.Inherit, 'done': Autonomy.Inherit},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list'})

			# x:605 y:463
			OperatableStateMachine.add('Say_To_Change_Name',
										LogState(text="Please make sure you updated the name of the trial", severity=Logger.REPORT_HINT),
										transitions={'done': 'Sets_Filename_And_Path_From_Rqt_Acquistion_Params'},
										autonomy={'done': Autonomy.Full})

			# x:646 y:544
			OperatableStateMachine.add('Sets_Filename_And_Path_From_Rqt_Acquistion_Params',
										VariableMultiSetNameAndPathFromParamState(prefix="", suffix="/set_name_and_path", filename_param="rqt_acquisition/activity_name", dirname_param="rqt_acquisition/save_path", description_param="rqt_acquisition/description_text"),
										transitions={'done': 'Start_Recording_Question_Mark', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'node_start_list'})

			# x:674 y:130
			OperatableStateMachine.add('Start_Parked_Nodes',
										VariableMultiServiceCallState(predicate="/start_now", prefix=""),
										transitions={'done': 'Wait_For_Ik_To_Be_Ready', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'multi_service_list': 'parked_nodes'})

			# x:684 y:629
			OperatableStateMachine.add('Start_Recording_Question_Mark',
										LogState(text="Is the calibration and the heading OK?\n Proceeding will start recording the trial", severity=Logger.REPORT_HINT),
										transitions={'done': 'Recording_trial'},
										autonomy={'done': Autonomy.Full})

			# x:924 y:802
			OperatableStateMachine.add('Trial_Failed',
										PlaySoundState(sound_file="/srv/host_data/fail.wav", retries=5, which_player="paplay"),
										transitions={'continue': 'Record_Another', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:921 y:693
			OperatableStateMachine.add('Trial_Finished',
										PlaySoundState(sound_file="/srv/host_data/end.wav", retries=5, which_player="paplay"),
										transitions={'continue': 'Record_Another', 'failed': 'Record_Another'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:679 y:212
			OperatableStateMachine.add('Wait_For_Ik_To_Be_Ready',
										WaitForMessages(topics_list="/ik/output_filtered", custom_message="Waiting for IK node to start", timeout=1000),
										transitions={'continue': 'Get_Ready_For_Calibration', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:679 y:375
			OperatableStateMachine.add('Calibrate_IK',
										MultiServiceCallState(multi_service_list="/ik", predicate="/calibrate", prefix="", wait_to_start=False, timeout=60),
										transitions={'done': 'Calibration_Complete', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	def find_pkg(self, pkg):
		return self.rospack.get_path(pkg)
	# [/MANUAL_FUNC]
