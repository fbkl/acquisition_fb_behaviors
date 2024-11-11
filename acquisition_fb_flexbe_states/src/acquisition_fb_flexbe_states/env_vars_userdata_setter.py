#!/usr/bin/env python

from flexbe_core import EventState, Logger
import traceback
import os

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
        super(MomentArmAndLibraryEnvSetterUserDataState, self).__init__(input_keys=["model","lib","should_load_ar","env_vars","common_vars"], output_keys=["env_vars"], outcomes=["done"])

        self._return_code = None

    def execute(self, userdata):
        '''
        Execute this state
        '''
        return self._return_code


    def on_enter(self, userdata):

        try:

          # Add the user data
          userdata.env_vars.update(userdata.common_vars)
          lib_file = ""
          lib_base_file, lib_ext =  os.path.splitext(userdata.lib)
          if lib_ext == '.so':
              lib_file =  lib_base_file
          elif lib_ext == '':
              lib_file = lib_base_file
              Logger.logwarn("For most cases I am expecting an .so ending, is this a correct file?")
          else:
              Logger.logerr(f"You gave me a file with a strange extension, are you sure the name is correct?\n{userdata.lib}")
          
          assert(userdata.model)
          assert(lib_file)
          userdata.env_vars.update(  {"MODEL_FILE": userdata.model, "MOMENT_ARM_LIB": lib_file, "USE_AR": userdata.should_load_ar})
          Logger.logdebug(f"[env_vars_userdata_setter] env_vars:  {userdata.env_vars}")
          self._return_code = 'done'
        except:
            traceback.print_exc()
            raise ValueError('UserDataState %s - invalid data ' % self.name)
