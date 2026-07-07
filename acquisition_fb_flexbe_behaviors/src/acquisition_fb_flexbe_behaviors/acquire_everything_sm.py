#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from acquisition_fb_flexbe_behaviors.bringup_vio_sm import bringup_vioSM
from acquisition_fb_flexbe_states.VENVtmux_setup_from_yaml_state import VENVTmuxSetupFromYamlState
from acquisition_fb_flexbe_states.check_if_files_were_saved_state import CheckFileSavedState
from acquisition_fb_flexbe_states.env_vars_userdata_setter import MomentArmAndLibraryEnvSetterUserDataState
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
	acquire using embeddable VIO behavior
- with tmux 
- IK using old heading 
- playing sounds
- now tries to add camera as well
- adds rqt_acquisition
	'''


	def __init__(self):
		super(Acquire_EverythingSM, self).__init__()
		self.name = 'Acquire_Everything'

		# parameters of this behavior
		self.add_parameter('run_vicon_controller', False)
		self.add_parameter('remove_path', '/srv/host_data')
		self.add_parameter('append_path', 'd:/ViconData')
		self.add_parameter('vicon_ip', '192.168.1.103')
		self.add_parameter('vicon_port', 1030)
		self.add_parameter('session_id', 'SESSION0')
		self.add_parameter('activity_name', 'walking1')
		self.add_parameter('subject_id', 'EX02RE')
		self.add_parameter('weight', 72)
		self.add_parameter('height', 1.70)
		self.add_parameter('combined_acquisition', True)
		self.add_parameter('use_ar_markers_in_ik', False)
		self.add_parameter('show_viz_extensive', False)
		self.add_parameter('record_rosbag', False)
		self.add_parameter('rosmaster', 'raspberrypi')
		self.add_parameter('run_vicon_bridge', True)
		self.add_parameter('vicon_dummy', True)

		# references to used behaviors
		self.add_behavior(bringup_vioSM, 'bringup_vio')

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
		ori_list = ["torso","radius_r"]
		calib_sound_file = "/srv/host_data/calib.wav"
		ik_yaml = "plus_ik.yaml"
		vicon_yaml = "vicon_only.yaml"
		vicon_vars = {"REMOVE":self.remove_path,"APPEND":self.append_path,"VICON_IP":self.vicon_ip,"VICON_PORT":self.vicon_port,"VICON_DUMMY":self.vicon_dummy}
		tmux_session_name = "testtt"
		model_dir = "/srv/shared/raquegopal/"
		model_name = "raquegopal_2026"
		model_file = f"{model_dir}{model_name}.osim"
		moment_arm_lib = f"{model_dir}libMomentArm_{model_name}"
		export_vars = {"ROSLAUNCH_SSH_UNKNOWN":"1","MACHINE":self.rosmaster,"MODEL_FILE":model_file,"BASE_BODY":"torso", "NAME_TAG":"upper","MOMENT_ARM_LIB":moment_arm_lib,"NUM_PROC_SO":4,"USE_AR":self.use_ar_markers_in_ik,"COMBINED_ACQUISITION":self.combined_acquisition}
		combined_perspective_file = self.find_pkg("rqt_acquisition")+"/VIOControl_Acquisition_small_tabs.perspective"
		common_vars = {"SHOW_VIZ_OTHER":self.show_viz_extensive,}
		ori_yaml_file = "vioarm.yaml"
		name_tag = "upper"
		vicon_bridge_yaml = "vicon_bridge.yaml"
		vicon_bridge_vars = {**export_vars,**vicon_vars}
		# x:1420 y:614, x:289 y:786
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.activity_save_dir = ""
		_state_machine.userdata.activity_save_name = ""
		_state_machine.userdata.node_start_list = []
		_state_machine.userdata.use_vicon_controller = self.run_vicon_controller
		_state_machine.userdata.parked_nodes = ["/vio/ik"]
		_state_machine.userdata.export_vars = export_vars
		_state_machine.userdata.should_load_ar = self.use_ar_markers_in_ik
		_state_machine.userdata.use_combined_acquisition = self.combined_acquisition
		_state_machine.userdata.vicon_vars = vicon_vars
		_state_machine.userdata.common_vars = common_vars
		_state_machine.userdata.save_file_list = []
		_state_machine.userdata.ori_list = ori_list
		_state_machine.userdata.use_vicon_bridge = self.run_vicon_bridge
		_state_machine.userdata.vicon_bridge_vars = vicon_bridge_vars

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
										TmuxSetupState(session_name=tmux_session_name, startup_dic={"acq":["rqt --standalone rqt_vioacq"]}),
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

			# x:1040 y:790
			OperatableStateMachine.add('Set_Vio_Units',
										MultiSetSomeParamState(multi_node_list=["rqt_acquisition"], param_to_set="ori_list", value_of_param=ori_list, check_if_nodes_exist=False),
										transitions={'done': 'finished', 'failed': 'failed'},
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
										transitions={'done': 'Set_Vio_Units', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})

			# x:124 y:459
			OperatableStateMachine.add('Combined_Acquistion_Perspective',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Combined_Perspective', 'false': 'Load_Rqt_Acquisition'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_combined_acquisition'})


		# x:953 y:222, x:68 y:409
		_sm_node_startup_2 = OperatableStateMachine(outcomes=['failed', 'ok'], input_keys=['node_start_list', 'use_vicon_controller', 'export_vars', 'should_load_ar', 'use_combined_acquisition', 'vicon_vars', 'common_vars', 'save_file_list', 'use_vicon_bridge', 'vicon_bridge_vars'], output_keys=['node_start_list', 'save_file_list'])

		with _sm_node_startup_2:
			# x:530 y:23
			OperatableStateMachine.add('Acquisition_Setup',
										_sm_acquisition_setup_1,
										transitions={'finished': 'Run_Vicon_Controller', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'export_vars': 'export_vars', 'should_load_ar': 'should_load_ar', 'use_combined_acquisition': 'use_combined_acquisition', 'common_vars': 'common_vars'})

			# x:483 y:324
			OperatableStateMachine.add('Load_IK_nodes',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+ik_yaml, append_node=["/vio/ik"], append_save_files=["_ik_"+name_tag]),
										transitions={'continue': 'Run_Vicon_Bridge', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'export_vars'})

			# x:372 y:548
			OperatableStateMachine.add('Load_Vicon_Bridge_AndIK',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+vicon_bridge_yaml, append_node=["/vicon/ik"], append_save_files=["_ik_vicon"+name_tag]),
										transitions={'continue': 'ok', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'vicon_bridge_vars'})

			# x:448 y:167
			OperatableStateMachine.add('Load_Vicon_Controller_Node',
										VENVTmuxSetupFromYamlState(session_name=tmux_session_name, startup_yaml=tmux_yaml_path+vicon_yaml, append_node=["/vicon_control"], append_save_files=[]),
										transitions={'continue': 'ORI_names_setter', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'node_start_list': 'node_start_list', 'save_file_list': 'save_file_list', 'load_env': 'vicon_vars'})

			# x:121 y:258
			OperatableStateMachine.add('ORI_names_setter',
										SetRosParamState(namespace_prefix="/vio/ik", param_dic={"imu_observation_order":ori_list}),
										transitions={'continue': 'Load_IK_nodes', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:240 y:375
			OperatableStateMachine.add('Run_Vicon_Bridge',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Vicon_Bridge_AndIK', 'false': 'ok'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_vicon_bridge'})

			# x:245 y:65
			OperatableStateMachine.add('Run_Vicon_Controller',
										CheckConditionState(predicate=lambda x: bool(x)),
										transitions={'true': 'Load_Vicon_Controller_Node', 'false': 'ORI_names_setter'},
										autonomy={'true': Autonomy.Off, 'false': Autonomy.Off},
										remapping={'input_value': 'use_vicon_controller'})



		with _state_machine:
			# x:85 y:37
			OperatableStateMachine.add('Set_Params_Weight_And_Delay',
										SetRosParamState(namespace_prefix="", param_dic={"/rqt_acquisition/weight":self.weight}),
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

			# x:371 y:31
			OperatableStateMachine.add('Node_Startup',
										_sm_node_startup_2,
										transitions={'failed': 'failed', 'ok': 'bringup_vio'},
										autonomy={'failed': Autonomy.Inherit, 'ok': Autonomy.Inherit},
										remapping={'node_start_list': 'node_start_list', 'use_vicon_controller': 'use_vicon_controller', 'export_vars': 'export_vars', 'should_load_ar': 'should_load_ar', 'use_combined_acquisition': 'use_combined_acquisition', 'vicon_vars': 'vicon_vars', 'common_vars': 'common_vars', 'save_file_list': 'save_file_list', 'use_vicon_bridge': 'use_vicon_bridge', 'vicon_bridge_vars': 'vicon_bridge_vars'})

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
										WaitForMessages(topics_list="/vio/ik/output_filtered", custom_message="Waiting for IK node to start", timeout=1000),
										transitions={'continue': 'Get_Ready_For_Calibration', 'failed': 'failed'},
										autonomy={'continue': Autonomy.Off, 'failed': Autonomy.Off})

			# x:662 y:24
			OperatableStateMachine.add('bringup_vio',
										self.use_behavior(bringup_vioSM, 'bringup_vio',
											parameters={'vio_yaml_file': ori_yaml_file}),
										transitions={'finished': 'Start_Parked_Nodes', 'failed': 'failed'},
										autonomy={'finished': Autonomy.Inherit, 'failed': Autonomy.Inherit},
										remapping={'vio_export_vars': 'export_vars', 'ori_list': 'ori_list'})

			# x:679 y:375
			OperatableStateMachine.add('Calibrate_IK',
										MultiServiceCallState(multi_service_list="/vio/ik", predicate="/calibrate", prefix="", wait_to_start=False, timeout=60),
										transitions={'done': 'Calibration_Complete', 'failed': 'failed'},
										autonomy={'done': Autonomy.Off, 'failed': Autonomy.Off})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	def find_pkg(self, pkg):
		return self.rospack.get_path(pkg)
	# [/MANUAL_FUNC]
