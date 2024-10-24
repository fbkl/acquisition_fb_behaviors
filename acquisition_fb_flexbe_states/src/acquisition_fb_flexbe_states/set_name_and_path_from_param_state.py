#!/usr/bin/env python
import rospy

from flexbe_core import EventState, Logger
from acquisition_of_raw_data import multiservice_plex
from opensimrt_msgs.srv import SetFileNameSrv, SetFileNameSrvRequest, SetFileNameSrvResponse

import re


class MultiSetNameAndPathFromParamState(EventState):
    '''

    sets path

    -- multi_service_list str[]     list of srvs
    -- prefix           str         prefix of srvs
    -- suffix           stf         suffix of srvs
    -- filename_param   str         The filename will be read from this param
    -- dirname_param    str         The dirname will be read from this param
    

    <= done 			Given time has passed.
    <= failed 				Example for a failure outcome.

    '''

    def __init__(self, multi_service_list, prefix, suffix, filename_param, dirname_param):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(MultiSetNameAndPathFromParamState, self).__init__(outcomes = ['done', 'failed'],)

        # Store state parameter for later use.

        self._filename_param = filename_param
        self._dirname_param = dirname_param
        if type(multi_service_list) == type(""):
            multi_service_list = [multi_service_list]

        self._multi_service_list = []
        for a_srv in multi_service_list:
            self._multi_service_list.append(prefix+a_srv+suffix)

        Logger.loginfo("received list: %s" % multi_service_list)
        self._multi_service_plex = multiservice_plex.MultiServiceCaller(self._multi_service_list, SetFileNameSrv(), SetFileNameSrvResponse())

        # The constructor is called when building the state machine, not when actually starting the behavior.
        # Thus, we cannot save the starting time now and will do so later.
        self._responses = None
        self._old_counter = None
        self._activity = ""

    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.

        if self._multi_service_plex.error_list == [] and not self._responses == None:
            #Logger.loginfo("responses ok:%s"%self._responses)
            return 'done' # One of the outcomes declared above.
        else:
            Logger.logwarn(str(self._responses))
            Logger.logwarn(str(self._multi_service_plex.error_list))
            return 'failed'


    def on_enter(self, userdata):


        ## does call

        # we maybe dont want this, so we can rerecord another?
        ##userdata.activity_counter +=1
        _file_name = rospy.get_param(self._filename_param)
        _save_dir = rospy.get_param(self._dirname_param)
        
        match = re.match(r"([a-z]+)([0-9]+)", _file_name, re.I)
        if match:
            items = match.groups()
            if len(items) >= 2:
                self._activity = items[:-1]
                self._old_counter = int(items[-1])


        req = SetFileNameSrvRequest()
        req.name = _file_name
        req.path = _save_dir
        Logger.log("my req msg: "+str(req),Logger.REPORT_HINT )
        _, self._responses = self._multi_service_plex(req)


    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.

        # we update the counter of the activity 
        self._old_counter+=1
        rospy.set_param(self._filename_param, f"{self._activity}{self._old_counter}" )

    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        pass

    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.

        pass # Nothing to do in this example.

