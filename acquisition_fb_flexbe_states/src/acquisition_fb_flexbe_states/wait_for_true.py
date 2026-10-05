#!/usr/bin/env python3
import rospy
import tf
from flexbe_core import EventState, Logger
import traceback
from std_msgs.msg import Bool
from threading import Thread, Lock

class WaitForTrueMessages(EventState):
    '''
    Wait for all the topics in the list to be publishing true messages

    -- topics_list 	list 	List of topics to check if messages are comming.
    -- custom_message str   Custom message to display while waiting for topic

    <= continue 			Given time has passed.
    <= failed 				Example for a failure outcome.

    '''

    def __init__(self, topics_list, custom_message = "", timeout=600):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(WaitForTrueMessages, self).__init__(outcomes = ['continue', 'failed'])

        # Store state parameter for later use.

        if type(topics_list) == type(""):
            topics_list = [topics_list]

        self._topics_list = []
        self._topics_list_names = topics_list
        self._custom_message = custom_message
        self._initial_topics_len = len(self._topics_list_names)
        self._initial_time = None
        self._timeout_time = rospy.Duration(timeout)
        self.mu = Lock()
        self.returns = [False]*self._initial_topics_len

        self._ran_once = False

    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.

        if self._ran_once:
            Logger.logerr('I only intended this to run once. If you want it to be able to run multiple times, this is a different state.')
            return 'failed'

        if rospy.Time.now() > self._initial_time + self._timeout_time:
            Logger.logerr("Timeout exceeded")
            return 'failed'

        #return 'continue'
        try:
            with self.mu:
                if all(self.returns):
                    self._ran_once = True
                    #self.returns = [False]*self._initial_topics_len ## claude wants this to be able to be run multiple times, so we should reset returns
                    return 'continue'
        except Exception as e:
            st = traceback.format_stack()
            #traceback.print_stack()
            Logger.logerr("I failed while waiting for topics: {}\n{}".format(str(e),str(st)))
            return 'failed'
    #@staticmethod
    def funny_cb(self, msg, i):
        Logger.loginfo(f"called funny callback {i}")
        if msg.data:
            with self.mu:
                self.returns[i] = True
        return

    def on_enter(self, userdata):
        # This method is called when the state becomes active, i.e. a transition from another state to this one is taken.
        # It is primarily used to start actions which are associated with this state.
        if self._custom_message:
            Logger.loghint(self._custom_message)
        else:
            Logger.loghint(f"Will spend {self._timeout_time.to_sec()}s looking for messages on the topics:\n{self._topics_list_names}")
        self._initial_time = rospy.Time.now()

    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.
        pass        


    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.
        i = 0
        for a_topic in self._topics_list_names:
            # i dont need to append anything....

            self._topics_list.append(
                    rospy.Subscriber(a_topic, Bool, callback=self.funny_cb, callback_args=i)
                    )
            i+=1

        for top in self._topics_list:
            Logger.loghint(f" {top} has  {top.get_num_connections}")
            Logger.loginfo(f" {top} has  {top.get_num_connections}")

    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.
        for top in self._topics_list:
                #proc.kill()
                #outs, errs = proc.communicate()
                top.unregister()
        
