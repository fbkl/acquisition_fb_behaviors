#!/usr/bin/env python
import rospy

from flexbe_core import EventState, Logger
from acquisition_of_raw_data import multiservice_plex
from opensimrt_msgs.srv import SetFileNameSrv, SetFileNameSrvRequest, SetFileNameSrvResponse
from std_srvs.srv import Empty

import re


class VariableMultiSetNameAndPathFromParamState(EventState):
    '''

    sets path

    -- multi_service_list str[]     list of srvs
    -- prefix           str         prefix of srvs
    -- suffix           stf         suffix of srvs
    -- filename_param   str         The filename will be read from this param
    -- dirname_param    str         The dirname will be read from this param
    

    <= done 			    Params set okay.
    <= failed 				Something failed.

    '''

    def __init__(self, prefix, suffix, filename_param, dirname_param):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(VariableMultiSetNameAndPathFromParamState, self).__init__(outcomes = ['done', 'failed'],
                                                        input_keys = ['multi_service_list'],)
        # Store state parameter for later use.

        self._filename_param = filename_param
        self._dirname_param = dirname_param
        self._multi_service_list = []
        self._prefix = prefix
        self._predicate = suffix
        self._activity = ""
        self._multi_service_plex = None
        self._old_counter = None
        self._acquisition_update = rospy.ServiceProxy("/rqt_acquisition/update_widgets", Empty)


    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.

        if not self._multi_service_plex:
            Logger.logerr("MULTISERVICEPLEX IS NONE???")
            return 'failed'
        if self._multi_service_plex.error_list == [] and not self._responses == None:
            #Logger.loginfo("responses ok:%s"%self._responses)
            return 'done' # One of the outcomes declared above.
        else:
            Logger.logwarn(str(self._responses))
            Logger.logwarn(str(self._multi_service_plex.error_list))
            return 'failed'


    def on_enter(self, userdata):

        if type(userdata.multi_service_list) == type(""):
            userdata.multi_service_list = [userdata.multi_service_list]

        for an_srv_name in userdata.multi_service_list:
            self._multi_service_list.append(self._prefix+an_srv_name+self._predicate)
        Logger.loginfo("received list of services to be called: %s" % self._multi_service_list)

        self._multi_service_plex = multiservice_plex.MultiServiceCaller(self._multi_service_list, SetFileNameSrv(), SetFileNameSrvResponse())


        ## does call

        # we maybe dont want this, so we can rerecord another?
        ##userdata.activity_counter +=1
        _file_name = rospy.get_param(self._filename_param)
        _save_dir = rospy.get_param(self._dirname_param)
        
        match = re.match(r"([a-z]+)([0-9]+)", _file_name, re.I)
        if match:
            Logger.loghint("found a trial counter, will try to add 1 to the next if possible")
            items = match.groups()
            if len(items) >= 2:
                self._activity = "".join(items[:-1])
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
        counter = ""
        if self._old_counter:
            counter = str(self._old_counter+1)
        rospy.set_param(self._filename_param, f"{self._activity}{counter}" )
        try:
            self._acquisition_update()
        except:
            Logger.logerr("count call rqt_acquisition/update_widgets service")

    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        pass

    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.

        pass # Nothing to do in this example.

