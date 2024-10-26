#!/usr/bin/env python
import rospy
import os
import subprocess
from flexbe_core import EventState, Logger


class PlaySoundState(EventState):
    '''

        Play a sound file using aplay.

    -- sound_file 	string 	Sound file to play.

    <= continue 			Sound file has ended.
    <= failed 				Example for a failure outcome.

    '''

    def __init__(self, sound_file, retries=5):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(PlaySoundState, self).__init__(outcomes = ['continue', 'failed'])

        # Store state parameter for later use.
        if os.path.exists(sound_file):
            self._sound_file = sound_file
        else:
            raise rospy.ROSException("no file")

        # The constructor is called when building the state machine, not when actually starting the behavior.
        self._p = None
        self._retries = retries
        self._tries = 0
        #self.order = ["init"]



    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.

            #print(rc)
        res = self._p.poll()
        #print(res)
        if res is not None: ## non blocking. will return None if process is still happening, allows to play longer sounds
            output, err = self._p.communicate(b"")
            if self._p.returncode == 0: 
                return 'continue' # One of the outcomes declared above.
            else:
                if self._tries < self._retries:
                    self.do_try()
                else:
                    Logger.logerr("Maximum number of retries reached.");
                    Logger.loginfo(output)
                    Logger.logerr(err)
                return 'failed'
        #print(self.order)
        #self.order.append("execute")

    def do_try(self):
        self._tries+=1
        self._p = subprocess.Popen(["aplay",self._sound_file], stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE)

    def on_enter(self, userdata):
        # This method is called when the state becomes active, i.e. a transition from another state to this one is taken.
        # It is primarily used to start actions which are associated with this state.

        # The following code is just for illustrating how the behavior logger works.
        # Text logged by the behavior logger is sent to the operator and displayed in the GUI.

        Logger.loginfo("Play!")
        self.do_try()
        #self.order.append("on_enter")
        #print(self.order)


    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.

        #self.order.append("on_exit")
        #print(self.order)
        pass # Nothing to do in this example.


    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        #self.order.append("on_start")
        #print(self.order)
        pass

    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.
        #self.order.append("on_stop")
        #print(self.order)

        pass # Nothing to do in this example.

