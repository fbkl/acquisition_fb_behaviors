#!/usr/bin/env python
import rospy

from flexbe_core import EventState, Logger


class SetRosParamState(EventState):
    '''
    The whole thing about parameter passing is driving me insane. There is a reason why ROS has a parameter server, please, use it

    -- namespace_prefix         string  Parameters will be set to this namespace
    -- param_dic 	            dict 	Dictionary of parameters to be set

    <= continue 			Parameter set correctly.
    <= failed 				Something went wrong.

    '''

    def __init__(self, namespace_prefix, param_dic):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(SetRosParamState, self).__init__(outcomes = ['continue', 'failed'])

        self._ok = True
        Logger.loginfo(repr(param_dic))
        if not type(param_dic) == type({"a":1}):
            Logger.logerr("incorrect parameter type for param_dic!")
            self._ok = False
        self._param_dic = param_dic

        self._namespace = namespace_prefix
        ## consider updating the dictinary instead

    def execute(self, userdata):
        if self._ok:
            return 'continue' # One of the outcomes declared above.
        return 'failed'

    def on_enter(self, userdata):
        # This method is called when the state becomes active, i.e. a transition from another state to this one is taken.
        # It is primarily used to start actions which are associated with this state.
        try:
            for param, value in self._param_dic.items():
                rospy.set_param(self._namespace+"/"+param, value)
        except:
            Logger.logerr(f"something went wrong while trying to set parameters {self._namespace} {repr(self._param_dic)}")
            self._ok = False
    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.

        pass # Nothing to do in this example.

    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        pass # Nothing to do in this example.


    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.
        for param, value in self._param_dic.items():
            rospy.delete_param(self._namespace+"/"+param)


