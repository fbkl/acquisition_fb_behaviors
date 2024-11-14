#!/usr/bin/env python
import rospy
import os
from flexbe_core import EventState, Logger
import glob
import traceback

class CheckFileSavedState(EventState):
    '''

    -- target_time 	float 	Time which needs to have passed since the behavior started.

    ># expected_files str[] List of files I am expected to find at a path
    -- filename_param str   param that has the activity name that i am looking for
    -- dirname_param  str   Param that has the path of the stuff i am looking for


    <= continue 			Given time has passed.
    <= failed 				Example for a failure outcome.

    '''

    def __init__(self, filename_param = "rqt_acquisition/activity_name", dirname_param = "rqt_acquisition/save_path", target_time = 5):
        # Declare outcomes, input_keys, and output_keys by calling the super constructor with the corresponding arguments.
        super(CheckFileSavedState, self).__init__(outcomes = ['continue', 'failed'],
                input_keys = ['expected_files'])

        self._file_param = filename_param
        self._dir_param = dirname_param

        self._file = ""
        self._dir = ""
        self._errors = []
        self._target_time = rospy.Duration(target_time)
        self._start_time = None

    def execute(self, userdata):
        # This method is called periodically while the state is active.
        # Main purpose is to check state conditions and trigger a corresponding outcome.
        # If no outcome is returned, the state will stay active.
        try:
            self._file = rospy.get_param(self._file_param)
            self._dir = rospy.get_param(self._dir_param)
            assert(self._file)
            assert(self._dir)

            ## now check if files actually exist
            files_found = {}
            files_missing = []
            Logger.loginfo(f"CheckFileSavedState dir: {self._dir}")
            Logger.loginfo(f"CheckFileSavedState file: {repr(self._file)}")
            Logger.loghint(f"CheckFileSavedState list of expected files: {repr(userdata.expected_files)}")
            assert(os.path.exists(self._dir))

            files_in_dir = glob.glob(os.path.join(self._dir,"*"))

            assert(type(userdata.expected_files) == type([]))
            for file in userdata.expected_files:
                found_this_file = False
                corresponding_file = ""
                for file_that_exist in files_in_dir:
                    Logger.loginfo(f"comparing file: {file_that_exist} to file {file} with additional requirement of having {self._file} in its name!")
                    if file in file_that_exist and self._file in file_that_exist:
                        corresponding_file = file_that_exist
                        found_this_file = True
                        break
                if found_this_file:
                    files_found.update({file:corresponding_file})
                else:
                    files_missing.append(file)
            Logger.loginfo(f"files_found: {repr(files_found)}")
            if rospy.Time.now() - self._start_time > self._target_time:
                if len(files_found) == 0:
                    self._errors.append("no files found")
                    Logger.logerr("NO FILE FOUND!!!!")
                if len(files_missing) != 0:
                    Logger.logerr(f"files_missing: {repr(files_missing)}")
                    self._errors.append(f"files_missing: {repr(files_missing)}")
                    return 'failed'
                else:
                    return 'continue'
            else:
                if len(files_missing) == 0:
                    return 'continue'


        except:
            Logger.logerr("Something failed while checking for files!")
            traceback.print_exc()

        if len(self._errors)>0:
            for i, err in enumerate(self._errors):
                Logger.logerr(str(i)+repr(err))
            self._errors = []

            return 'failed'
        ## I did something wrong here,
        #return 'continue'

    def on_enter(self, userdata):
        # This method is called when the state becomes active, i.e. a transition from another state to this one is taken.
        # It is primarily used to start actions which are associated with this state.

        time_to_wait = (self._target_time - (rospy.Time.now() - self._start_time)).to_sec()

        if time_to_wait > 0:
            Logger.loginfo('Need to wait for %.1f seconds.' % time_to_wait)

    def on_exit(self, userdata):
        # This method is called when an outcome is returned and another state gets active.
        # It can be used to stop possibly running processes started by on_enter.

        pass # Nothing to do in this example.


    def on_start(self):
        # This method is called when the behavior is started.
        # If possible, it is generally better to initialize used resources in the constructor
        # because if anything failed, the behavior would not even be started.

        self._start_time = rospy.Time.now()

    def on_stop(self):
        # This method is called whenever the behavior stops execution, also if it is cancelled.
        # Use this event to clean up things like claimed resources.

        pass # Nothing to do in this example.

