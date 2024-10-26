#!/usr/bin/env python

from flexbe_core import EventState, Logger
import traceback
'''
Created on 14-Feb-2018

@author: David Conner
'''

class MomentArmAndLibraryEnvSetterUserDataState(EventState):
    '''
    Implements a state that defines user data

    #< model               the model file 
    #< lib                 the lib file 
    #< should_load_ar      desc
    #< env_vars             desc
    #> env_vars            The generated user_vars

    <= done                Created the user data
    '''


    def __init__(self ):
        '''
        Constructor
        '''
        super(MomentArmAndLibraryEnvSetterUserDataState, self).__init__(input_keys=["model","lib","should_load_ar","env_vars"], output_keys=["env_vars"], outcomes=["done"])

        self._return_code = None

    def execute(self, userdata):
        '''
        Execute this state
        '''
        return self._return_code


    def on_enter(self, userdata):

        try:

          # Add the user data
          userdata.env_vars.update(  {"MODEL_FILE": userdata.model, "MOMENT_ARM_LIB": userdata.lib, "USE_AR": userdata.should_load_ar})
          self._return_code = 'done'
        except:
            traceback.print_exc()
            raise ValueError('UserDataState %s - invalid data ' % self.name)
