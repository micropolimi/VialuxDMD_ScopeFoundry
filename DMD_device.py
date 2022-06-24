# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 18:12:05 2021
@authors: Elena Corbetta, Andrea Bassi. Politecnico di Milano
"""

from ALP4 import *
import numpy as np
import time

class VialuxDmdDevice(object):
    
    def __init__(self):
        
        dmd = ALP4(version = '4.3',libDir = 'C:\Program Files\ALP-4.3\ALP-4.3 API')
        # TODO autoomatic link to ALP library dir
        dmd.Initialize()
        dmd.DevControl(ALP_TRIGGER_EDGE, ALP_EDGE_RISING)
        dmd.DevControl(ALP_SYNCH_POLARITY, ALP_LEVEL_HIGH)
        self.dmd = dmd
        
    def get_width(self):
        w = self.dmd.nSizeX
        return w

    def get_height(self):
        h = self.dmd.nSizeY
        return h
    
    def get_info_device(self):
        i = 'Serial number: ' + str(self.dmd.DevInquire(ALP_DEVICE_NUMBER)) + '- Version: ' + str(self.dmd.DevInquire(ALP_VERSION))
        return i
    
    def get_available_memory(self):
        return str(self.dmd.DevInquire(ALP_AVAIL_MEMORY))
            
    def allocate_memory(self, npatt, bitDepth = 8):
        idSeq = self.dmd.SeqAlloc(nbImg = npatt,         #number of images in the sequence
                                  bitDepth = bitDepth)   #quantization of the image (1-8)
        
    def load_patterns(self, stack):
        """
        Loads a stack of images onto the DMD, after memory has been allocated.
        Patterns are 2D matrices defined in the (x,y) plane.
        """
        self.dmd.SeqPut(imgData = stack)

    def invert_pattern(self, invert):
        if invert == True:
            self.dmd.ProjControl(ALP_PROJ_INVERSION, not ALP_DEFAULT)
        
    
    def set_timing(self, Tpicture, Tacq, SynchWidth, SynchDelay=0, TriggDelay=0):
        Tpicture = int(Tpicture*1000) # us
        Till = int(Tacq*1000) # us
     
        self.dmd.SetTiming(illuminationTime=Till,          #display time of a single image [us]
                           pictureTime=Tpicture,           #time between the start of 2 images
                           synchDelay= int(SynchDelay),          #delay between the start of the output sync pulse and the start of the display
                           synchPulseWidth= int(SynchWidth),     #duration of the sync output pulse
                           triggerInDelay= int(TriggDelay))      #length of trigger signal [us], default=0
    
    
    
    def set_projection_mode(self, proj_mode='master'):
        if proj_mode == 'master':
            self.dmd.ProjControl(ALP_PROJ_MODE, ALP_MASTER)
        elif proj_mode == 'slave':
            self.dmd.ProjControl(ALP_PROJ_MODE, ALP_SLAVE)
    
    def set_sequence(self, first_frame, last_frame, nrep):
        self.dmd.SeqControl(ALP_FIRSTFRAME, first_frame)
        self.dmd.SeqControl(ALP_LASTFRAME, last_frame)
        self.dmd.SeqControl(ALP_SEQ_REPEAT, nrep)
        
    
    def set_trigger(self, trigger_mode = 'master'):
        self.dmd.DevControl(ALP_TRIGGER_EDGE, ALP_EDGE_RISING)
        self.dmd.DevControl(ALP_SYNCH_POLARITY, ALP_LEVEL_HIGH)
    
    def run_sequence(self, proj_continuous=False):
        self.dmd.Run(loop=proj_continuous)
        print("Start Projection")
    
    # def free_memory(self):
    #     self.dmd.Free() # deallocates the memory, removing also the ALPlib
                     
    def free_sequence(self):
        self.dmd.FreeSeq()
            
    def stop(self):
        self.dmd.Halt()
    
    def close(self):
        self.dmd.Halt()
        #De-allocate the device
        self.dmd.Free()

if __name__ == "__main__":
    dev = VialuxDmdDevice()
    
    try:
        nx = 1024
        ny = 768
        nz = 30
        
        stack = np.random.random((nz,ny,nx))
        
        
        # dev.allocate_memory(npatt = nz, bitDepth = 8)
        # dev.set_timing()
        # dev.set_trigger()
        # dev.load_patterns(stack)
        # dev.run_sequence()
    
    except Exception as e:
        print(e)
        
    finally:
        dev.close()
    
    
