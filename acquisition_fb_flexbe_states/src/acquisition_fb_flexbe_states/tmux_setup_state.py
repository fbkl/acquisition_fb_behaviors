#!/usr/bin/env python
import rospy
import traceback
from flexbe_core import EventState, Logger
from tmux_launch.tmux_session_manager import *

class TmuxSetupState(EventState):
    '''
        starts tmux

    -- startup_dic 	dict 	

    <= continue 			Given time has passed.
    <= failed 				Example for a failure outcome.

    '''

    def __init__(self, session_name, startup_dic):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(TmuxSetupState, self).__init__(outcomes = ['continue', 'failed'])

        # Store state parameter for later use.
        self._session_name = session_name
        self._startup_dic = startup_dic
        Logger.loghint("__init before creating TmuxManager")
        self._tmux_manager = TmuxManager(self._session_name)
        ## TODO: this only works if you have a single session
        Logger.loghint("__init before getting Session")
        self._tmux_manager.session = self._tmux_manager.srv.sessions.get()
    def execute(self, userdata):
        return 'continue' # One of the outcomes declared above.


    def on_enter(self, userdata):
        ##manager already exists and also the session, we only attach and create the windows
        Logger.loghint("on_enter before creating some windows")
        try:
            create_some_windows(window_dic=self._startup_dic, some_manager= self._tmux_manager)
        except Exception as e:
            Logger.logerr(repr(e))
            traceback.print_exc()
            return 'failed'
        ## I should detect failures, shouldnt I?


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

