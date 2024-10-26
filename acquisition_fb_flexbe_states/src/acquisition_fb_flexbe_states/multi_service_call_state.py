#!/usr/bin/env python
import rospy

from flexbe_core import EventState, Logger
from acquisition_of_raw_data import multiservice_plex
from std_srvs.srv import EmptyRequest
import traceback

class MultiServiceCallState(EventState):
    '''
    THis will call multiple services on a list with EmptyRequest std_srvs messages

    -- prefix               str     string that will be a prefix of all services in the list
    -- multi_service_list 	list 	list of services to be called.
    -- predicate            str     name that will be appended to every srv

    <= done 			    it worked..
    <= failed 				some error occurred when calling services.

    '''

    def __init__(self, multi_service_list, predicate,prefix,wait_to_start=False,timeout=60):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(MultiServiceCallState, self).__init__(outcomes = ['done', 'failed'])

        # Store state parameter for later use.
        self._multi_service_list = []
        self._predicate = predicate
        self._prefix = prefix
        if type(multi_service_list) == type(""):
            multi_service_list = [multi_service_list]

        for an_srv_name in multi_service_list:
            self._multi_service_list.append(self._prefix+an_srv_name+self._predicate)
        Logger.loginfo("received list of services to be called: %s" % self._multi_service_list)
        self._multi_service_plex = multiservice_plex.MultiServiceCaller(self._multi_service_list, wait_to_start=wait_to_start, wait_for_responses = True, timeout=rospy.Duration(timeout))

        # The constructor is called when building the state machine, not when actually starting the behavior.
        # Thus, we cannot save the starting time now and will do so later.
        self._start_time = None

    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.

#		if rospy.Time.now() - self._start_time > self._multi_service_list:
        if self._multi_service_plex.error_list == []:
            return 'done' # One of the outcomes declared above.
        else:
            error_message = ""
            for error_msgs in self._multi_service_plex.error_list:
                error_message+= error_msgs
                error_message+= "\n"

            Logger.logerr(error_message)
            return 'failed'


    def on_enter(self, userdata):
        # This method is called when the state becomes active, i.e. a transition from another state to this one is taken.
        # It is primarily used to start actions which are associated with this state.

        # The following code is just for illustrating how the behavior logger works.
        # Text logged by the behavior logger is sent to the operator and displayed in the GUI.

        #time_to_wait = (self._multi_service_list - (rospy.Time.now() - self._start_time)).to_sec()

        #if time_to_wait > 0:
        #	Logger.loginfo('Need to wait for %.1f seconds.' % time_to_wait)

        ## does call
        try:
            self._multi_service_plex(EmptyRequest())
        except:
            
            traceback.print_exc()
            return 'failed'


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

