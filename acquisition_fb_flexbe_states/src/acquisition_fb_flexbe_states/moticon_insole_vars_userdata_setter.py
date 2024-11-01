#!/usr/bin/env python

from flexbe_core import EventState, Logger
import traceback
'''
Created on 14-Feb-2018

@author: David Conner
'''

class MoticonInsoleSetterUserDataState(EventState):
    '''
    Implements a state that defines user data

    #< insole_model             For moticon insoles those begin with S1 to S9
    #< grf_origin_z_offset      The vertical distance of the force applied (depends on the thickness of the shoe and the insole sensor)
    #< insole_vars              desc
    #> insole_vars              The generated user_vars

    <= done                     Created the user data
    '''


    def __init__(self ):
        '''
        Constructor
        '''
        super(MoticonInsoleSetterUserDataState, self).__init__(input_keys=["insole_model","insole_vars"], output_keys=["insole_vars","insole_length"], outcomes=["done"])

        self._return_code = None

    def execute(self, userdata):
        '''
        Execute this state
        '''
        return self._return_code


    def on_enter(self, userdata):

        try:

          # Add the user data

          # we do a switch statement here with the insole model sizes. 
          ## TODO: this is specific for the moticon insoles. i don't have another type, so I won't bother to make this general
          # I could have made it a yaml file and pointed it to the insole package, 

          ## values from the moticon datasheet
          foot_width_mm = None
          foot_length_mm = None
          grf_origin_z_offset = 0 
          Logger.logwarn("Attention, the height offset of the force was set to zero, this is probably not accurate.")
          if "S1" in userdata.insole_model:
                Logger.loginfo("Model S1 chosen")
                foot_width_mm = 80.2
                foot_length_mm = 214.9
          if "S2" in userdata.insole_model:
                Logger.loginfo("Model S2 chosen")
                foot_width_mm = 83.4
                foot_length_mm = 225.6
          if "S3" in userdata.insole_model:
                Logger.loginfo("Model S3 chosen")
                foot_width_mm = 86.7
                foot_length_mm = 236.8
          if "S4" in userdata.insole_model:
                Logger.loginfo("Model S4 chosen")
                foot_width_mm = 90.2
                foot_length_mm = 248.6
          if "S5" in userdata.insole_model:
                Logger.loginfo("Model S5 chosen")
                foot_width_mm = 93.8
                foot_length_mm = 261.1
          if "S6" in userdata.insole_model:
                Logger.loginfo("Model S6 chosen")
                foot_width_mm = 97.5
                foot_length_mm = 274.2
          if "S7" in userdata.insole_model:
                Logger.loginfo("Model S7 chosen")
                foot_width_mm = 101.4
                foot_length_mm = 288.0
          if "S8" in userdata.insole_model:
                Logger.loginfo("Model S8 chosen")
                foot_width_mm = 105.5
                foot_length_mm = 302.4
          if "S9" in userdata.insole_model:
                Logger.loginfo("Model S9 chosen")
                foot_width_mm = 109.7
                foot_length_mm = 317.5

          userdata.insole_vars.update(  {"FOOT_WIDTH": foot_width_mm/1000., "FOOT_LENGTH": foot_length_mm/1000., "GRF_ORIGIN_Z_OFFSET":grf_origin_z_offset })
          userdata.insole_length = foot_length_mm/1000
          Logger.logdebug(f"[insole_vars_userdata_setter] insole_vars:  {userdata.insole_vars}")
          self._return_code = 'done'
        except:
            traceback.print_exc()
            raise ValueError('UserDataState %s - invalid data ' % self.name)
