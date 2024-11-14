#!/usr/bin/env python
import rospy
import os
from flexbe_core import EventState, Logger


class HostAliveState(EventState):
    '''
    HostAlive for a state to demonstrate which functionality is available for state implementation.
    This example lets the behavior wait until the given target_time has passed since the behavior has been started.

    -- hostname 	str 	name or ip.
    -- waittime 	float 	wait time.

    <= continue 			Given time has passed.
    <= failed 				HostAlive for a failure outcome.

    '''

    def __init__(self, hostname="", waittime=1000):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(HostAliveState, self).__init__(outcomes = ['continue', 'failed'])

        self._hostname = hostname
        self._target_time = rospy.Duration(waittime)
        self.found_host = False


    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.

        if os.system("ping -c 1 -W " + str(0.1) + " " +
                self._hostname + " > /dev/null 2>&1") is 0:
            self.found_host = True
            return 'continue'
        if rospy.Time.now() - self._start_time > self._target_time:
            return 'failed'



    def on_enter(self, userdata):
        # This method is called when the state becomes active, i.e. a transition from another state to this one is taken.
        # It is primarily used to start actions which are associated with this state.

        # The following code is just for illustrating how the behavior logger works.
        # Text logged by the behavior logger is sent to the operator and displayed in the GUI.

        assert isinstance(self._hostname, str), \
                "IP/hostname must be provided as a string."
        #arg i hate this, its vulnerable to code injection.



    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.

        pass # Nothing to do in this example.


    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        # In this example, we use this event to set the correct start time.
        self._start_time = rospy.Time.now()


    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.

        pass # Nothing to do in this example.

