#!/usr/bin/env python
import rospy

from flexbe_core import EventState, Logger
from tmux_launch.tmux_session_manager import *

import yaml
import os
import re

class VENVTmuxSetupVariableVIOState(EventState):
    '''
        starts tmux
§
    -- startup_yaml 	file   This is a dict read from a yaml file  	

    <= continue 			Given time has passed.
    <= failed 				Example for a failure outcome.

    '''

    def __init__(self, session_name, startup_yaml,append_node=[],append_save_files=[]):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(VENVTmuxSetupVariableVIOState, self).__init__(outcomes = ['continue', 'failed'],
                input_keys = ["node_start_list","save_file_list","vio_units", 'load_env'],
                output_keys = ["node_start_list","save_file_list"])


        # Store state parameter for later use.
        self._loading= False
        self._session_name = session_name
        self._errors= []
        Logger.loghint(f"im trying to read this file: {startup_yaml}")
        self._append_nodes = append_node
        if not os.path.exists(startup_yaml):
            Logger.logerr("file %s does not exist!"%startup_yaml)
            raise Exception('failed:'+__file__)

        with open(startup_yaml) as stream:
            try:
                self._startup_dic = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                self._errors.append(exc)
                Logger.logerr(repr(exc))
                #print(exc)

        self._startup_file = startup_yaml
        ## TODO: this only works if you have a single session
        self._tmux_manager = TmuxManager(self._session_name)
        if not self._tmux_manager.srv.sessions:
            raise(RuntimeError(f"{__file__}: I need a previously setup tmux session already running to connect to!\n If you keep running it like this you won't be able to see any of the logs, which is the whole point of this thing."))
        found = False
        for ss in self._tmux_manager.srv.sessions:
            if ss.name == self._session_name:
                self._tmux_manager.session = ss
                found = True
                break
        if not found:
            raise(RuntimeError(f"could not find session '{session_name}'"))
   
        self._append_files = append_save_files

    def execute(self, userdata):
        if self._loading:
            return
        if self._errors:
            return 'failed'
        else:
            return 'continue' # One of the outcomes declared above.

    @staticmethod
    def parse_dict(startup_dict,units):
        final_startup_dict = {}
        regex_unit = re.compile("{UNIT}")
        regex_machine = re.compile("{MACHINE}")
        for key, cmds in startup_dict.items():
            #print(key,cmds)
            #print("¤"*40)
            for cmd in cmds:
                complete_list = []
                if "{UNIT}" in cmd:
                    for a_unit,in_a_machine in units.items():
                        new_str = cmd
                        #print(f"inital cmd: {new_str}")
                        new_str = regex_unit.sub(a_unit,cmd)
                        new_str = regex_machine.sub(in_a_machine,new_str)
                        #print(f"updated cmd: {new_str}")
                        if key in final_startup_dict:
                            complete_list = final_startup_dict[key]
                        complete_list.append(new_str)
                        #print(f"complete list: {complete_list}")
                else:
                    if key in final_startup_dict:
                        complete_list = final_startup_dict[key]
                    complete_list.append(cmd)
                final_startup_dict.update({key:complete_list})
                #print(f"final startup dict updated for the current cmd:\n {final_startup_dict}")
        return final_startup_dict

    def on_enter(self, userdata):
        rospy.loginfo("envs:"+repr(userdata.load_env))
        self._tmux_manager.load_env=userdata.load_env

        userdata.node_start_list.extend(self._append_nodes) 
        ##manager already exists and also the session, we only attach and create the windows
        self._loading = True
        ## Update the vio units

        final_startup_dict = self.parse_dict(self._startup_dic, userdata.vio_units)
        create_some_windows(window_dic=final_startup_dict, some_manager= self._tmux_manager)
        ## I should detect failures, shouldnt I?
        self._loading = False
        userdata.save_file_list.extend(self._append_files)
        
    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.

        pass # Nothing to do in this example.


    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        # In this example, we use this event to set the correct start time.
        pass

    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.

        self._tmux_manager.close_own_windows()

    def test(self,vio_units):

        final_startup_dict = self.parse_dict(self._startup_dic, vio_units)
        print(final_startup_dict)

if __name__ == '__main__':
    import rospy
    rospy.init_node("a")
    vio_units = {
            "torso":"silver",
            "radius":"rpi5-ubuntu",
            "right_leg":"imaginary_pi1",
            "right_umbilicus":"imaginary_pi2",
            "right_wing":"imaginary_pi3",
            "right_purse":"imaginary_pi4",
            }
    a = VENVTmuxSetupVariableVIOState("testtt", "../../../../acquisition_of_raw_data/config/vioarm.yaml")
    a.test(vio_units)
