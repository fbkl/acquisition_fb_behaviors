#!/usr/bin/env python

from flexbe_core import EventState, Logger
import rospy
import traceback

'''
Created on 14-Feb-2018

@author: David Conner
'''

class UserDataFromParamsState(EventState):
    '''
    Implements a state that defines user data

    -- param_path          Param path to read User data from
    -- data_property_name                Userdata property that will be set

    #> param_path          Param path to read User data from

    <= done                Created the user data
    '''


    def __init__(self, param_path, data_property_name ):
        '''
        Constructor
        '''
        super(UserDataFromParamsState, self).__init__( output_keys=[data_property_name], outcomes=["done"])

        self._data_property_name = data_property_name 
        self._param_path = param_path
        self._return_code = None

    def execute(self, userdata):
        '''
        Execute this state
        '''
        return self._return_code


    def on_enter(self, userdata):

        try:
          # Add the user data
          #userdata.ros_params = self._my_data
          self._my_data = rospy.get_param(self._param_path)

          Logger.loghint(f"param im reading: {self._param_path}\nvalue: {self._my_data}\nStored in: userdata.{self._data_property_name}")
          setattr(userdata, self._data_property_name, self._my_data)
          self._return_code = 'done'
        except Exception as e:
            Logger.logerr(repr(e))
            traceback.print_exc()
            raise ValueError('UserDataState %s - invalid data ' % self.name)
