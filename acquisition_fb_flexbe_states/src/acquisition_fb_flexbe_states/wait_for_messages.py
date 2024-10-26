#!/usr/bin/env python3
import rospy
import tf
from flexbe_core import EventState, Logger
import traceback
## there is no message traits, so we cheat with subprocess
import subprocess


class WaitForMessages(EventState):
    '''
    Wait for all the topics in the list to be publishing

    -- topics_list 	list 	List of topics to check if messages are comming.
    -- custom_message str   Custom message to display while waiting for topic

    <= continue 			Given time has passed.
    <= failed 				Example for a failure outcome.

    '''

    def __init__(self, topics_list, custom_message = "", timeout=600):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(WaitForMessages, self).__init__(outcomes = ['continue', 'failed'])

        # Store state parameter for later use.

        if type(topics_list) == type(""):
            topics_list = [topics_list]

        self._topics_list = []
        self._topics_list_names = topics_list
        self._custom_message = custom_message
        self._initial_topics_len = len(self._topics_list_names)
        self._initial_time = None
        self._timeout_time = rospy.Duration(timeout)

    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.
        if len(self._topics_list) == 0:
            return 'continue'
        if rospy.Time.now() > self._initial_time + self._timeout_time:
            Logger.logerr("Timeout exceeded")
            return 'failed'

        #return 'continue'
        try:

            for a_topic, a_topic_name in zip(self._topics_list, self._topics_list_names):
                #Logger.loghint(f"Looking for topics from {a_topic}")
                res = a_topic.poll()
                if res is not None: ## non blocking. will return None if process is still happening, allows to play longer sounds
                    output, err = a_topic.communicate(b"")
                    if a_topic.returncode == 0: 
                        Logger.loghint(f"rostopic echo for topic [{a_topic_name}] returned a message!")
                        self._topics_list.remove(a_topic)
                        break
                    else:
                        Logger.loginfo(output)
                        Logger.logerr(err)
                        return 'failed'
                else:
                    #Logger.loghint(f"rostopic echo for topic {a_topic} is still running")
                    pass

        except Exception as e:
            return 'continue'
        #st = traceback.format_stack()
            #traceback.print_stack()
            Logger.logerr("I failed while waiting for topics: {}\n{}".format(str(e),str(st)))
            return 'failed'


    def on_enter(self, userdata):
        # This method is called when the state becomes active, i.e. a transition from another state to this one is taken.
        # It is primarily used to start actions which are associated with this state.
        if self._custom_message:
            Logger.loghint(self._custom_message)
        else:
            Logger.loghint(f"Will spend {self._timeout_time.to_sec()}s looking for messages on the topics:\n{self._topics_list_names}")
        for a_topic in self._topics_list_names:
            self._topics_list.append(
                    subprocess.Popen(["rostopic","echo","-n","1",a_topic], stdin= subprocess.PIPE, stdout= subprocess.PIPE, stderr= subprocess.PIPE)
                    )
        self._initial_time = rospy.Time.now()

    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.

        pass # Nothing to do in this example.


    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        pass


    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.

        for proc in self._topics_list:
                proc.kill()
                outs, errs = proc.communicate()

