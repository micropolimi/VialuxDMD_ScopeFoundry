# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 18:12:05 2021
@authors: Elena Corbetta, Andrea Bassi. Politecnico di Milano
"""

from ScopeFoundry import HardwareComponent
from VialuxDMD_ScopeFoundry.DMD_device import VialuxDmdDevice


class VialuxDmdHW(HardwareComponent):
    name = 'VialuxDmdHW'
    
    def setup(self):
        # create Settings (aka logged quantities)       
        self.info = self.settings.New(name='info', dtype=str)
        self.avail_memory = self.settings.New(name='avail_memory', dtype=str, ro=True)
        self.width = self.settings.New(name='width', dtype=int, ro=True,unit='px')
        self.height = self.settings.New(name='height', dtype=int, ro=True,unit='px')
        self.projection_mode = self.settings.New(name='projection_mode', dtype=str, choices=('master', 'slave'), ro=False)
        self.proj_continuous = self.settings.New(name='proj_continuous', dtype=bool, ro=False, reread_from_hardware_after_write=True)
        self.invert_pattern = self.settings.New(name='invert_pattern', dtype=bool, ro=False)
        self.picture_period = self.settings.New(name='picture_period', dtype=float, initial=1000, unit='ms', ro=False, reread_from_hardware_after_write=True)
        self.time_on = self.settings.New(name='time_on', dtype=float, initial=900, unit='ms', spinbox_step = 0.1, ro=False, reread_from_hardware_after_write=True)
        self.synch_pulse_width = self.settings.New(name='synch_pulse_width', dtype=float,
                                                    initial=100, unit='us', ro=False)
        self.synch_delay = self.settings.New(name='synch_delay', dtype=float, initial=0,  unit='us', ro=False)
        self.trigger_in_delay = self.settings.New(name='trigger_in_delay', dtype=float, initial=0,  unit='us', ro=False)
        self.pattern_num = self.settings.New(name='pattern_num',initial= 10, vmin=1, spinbox_step = 1, dtype=int, ro=False)
        self.first_frame = self.settings.New(name='first_frame', dtype=int, initial=0,
                                             vmin=0, spinbox_step=1, ro=False, reread_from_hardware_after_write=True)
        self.last_frame = self.settings.New(name='last_frame', dtype=int, initial=self.settings.pattern_num.val-1,
                                             vmin=0, spinbox_step=1, ro=False, reread_from_hardware_after_write=True)#, vmax=self.settings.pattern_num.val-1)
        self.loop_number = self.settings.New(name='loop_number', dtype=int, initial=1,
                                             vmin=1, spinbox_step=1, ro=False, reread_from_hardware_after_write=True)
        self.repeat_each_pattern = self.settings.New(name='repeat_each_pattern', dtype=int, initial=1,
                                             vmin=1, spinbox_step=1, ro=False, reread_from_hardware_after_write=True)
        
        # self.add_operation('GenerateRandomPatterns', self.generate_random_patterns)
        self.add_operation('ImportSequence', self.import_sequence)
        self.add_operation('GenerateSequence', self.generate_sequence)
        self.add_operation('RunSequence', self.run_sequence)
        self.add_operation('FreeSequence', self.free_sequence)
        self.add_operation('Stop', self.stop)
        self.add_operation('Exit', self.exit)        
       
    def connect(self):
        # create an instance of the Device
        self.vialux = VialuxDmdDevice()      
        # connect settings to Device methods
        self.info.hardware_read_func = self.vialux.get_info_device
        self.avail_memory.hardware_read_func = self.vialux.get_available_memory
        self.height.hardware_read_func = self.vialux.get_height
        self.width.hardware_read_func = self.vialux.get_width
        self.invert_pattern.hardware_set_func = self.vialux.invert_pattern
        # self.pattern_num.hardware_set_func = self.vialux.allocate_memory
        self.projection_mode.hardware_set_func = self.vialux.set_projection_mode
        self.picture_period.hardware_set_func = self.set_timing_limits
        self.time_on.hardware_set_func = self.set_timing_limits
        self.synch_delay.hardware_set_func = self.set_timing_limits
        self.synch_pulse_width.hardware_set_func = self.set_timing_limits
        self.read_from_hardware()

      
    def set_timing_limits(self, *args): #TODO check if time_on needs reread_from_hardware_after_write
        """
        see ALP-4 Application Programming Interface for understanding the constants
        """
        self.picture_period.change_min_max(0.046, 10000) # ms
        
        time_on_max = self.settings.picture_period.val - 0.1 # ms
        self.settings.time_on.change_min_max(0, time_on_max)
        
        delay_max = min(130000, (self.settings.picture_period.val-self.settings.time_on.val-0.002)*1000) #us
        self.settings.synch_delay.change_min_max(0,delay_max ) 
    
        
        synch_pulse_width_min = 1 # us 
        synch_pulse_width_max = (self.settings.picture_period.val -0.001)*1000 #us
        self.settings.synch_pulse_width.change_min_max(synch_pulse_width_min, synch_pulse_width_max)
        
        trigger_in_delay_max = min(130000, (self.settings.picture_period.val-self.settings.synch_pulse_width.val-0.001)*1000) #us 
        self.trigger_in_delay.change_min_max(0, trigger_in_delay_max )
        
        
        
        
    def disconnect(self):
        if hasattr(self, 'vialux'):
            self.vialux.close() 
            del self.vialux
            
        for lq in self.settings.as_list():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
    
    def import_sequence(self):
        import numpy as np
        from skimage import io
        from easygui import fileopenbox
        tiffile = fileopenbox(msg="choose TIFF stack",title="Choose stack",
                              default = "C:/Programmi laboratorio/Python/VialuxDMDlibraries/*.tif",filetypes="*.tif")
        print("Tiff stack: " + tiffile)
        imgSeq = io.imread(tiffile)
        npatt,ly,lx = imgSeq.shape
        
        print(imgSeq.shape)
        
        padx = int((self.vialux.get_height() - lx)/2)
        pady = int((self.vialux.get_width() - ly)/2)
        print(self.vialux.get_height())
        print(self.vialux.get_width())
        
        print(padx)
        print(pady)
        imgSeq = np.pad(imgSeq,((0,0),(pady,pady),(padx,padx)),'constant')
        
        # Transpose the image
        imgSeq = imgSeq.swapaxes(1,2).copy()
        # pattern = pattern.swapaxes(0,2)
        # imgSeq = pattern
        npatt,ly,lx = imgSeq.shape
        
        self.vialux.allocate_memory(npatt=npatt, bitDepth = 8)
        self.vialux.load_patterns(imgSeq)
        self.settings['avail_memory'] = self.vialux.get_available_memory()
        self.settings['pattern_num'] = npatt
        self.settings['last_frame'] = npatt-1
        
    # def run_sequence(self):
    #     Tpic = self.settings.picture_period.val
    #     Tacq = self.settings.time_on.val
    #     Swidth = self.settings.synch_pulse_width.val
    #     Sdelay = self.settings.synch_delay.val
    #     Tdelay = self.settings.trigger_in_delay.val
        
    #     fframe = self.settings.first_frame.val
    #     lframe = self.settings.last_frame.val
    #     nloop = self.settings.loop_number.val
    #     nrep = self.settings.repeat_each_pattern.val
        
    #     proj_cont = self.settings.proj_continuous.val
        
    #     self.vialux.set_timing(Tpic, Tacq, Swidth, Sdelay, Tdelay)
    #     self.vialux.set_sequence(fframe, lframe, nloop)
    #     self.vialux.set_trigger()
    #     self.vialux.run_sequence(proj_cont)
        
        
    def run_sequence(self):
        Tpic = self.settings.picture_period.val
        Tacq = self.settings.time_on.val
        Swidth = self.settings.synch_pulse_width.val
        Sdelay = self.settings.synch_delay.val
        Tdelay = self.settings.trigger_in_delay.val
        
        fframe = self.settings.first_frame.val
        lframe = self.settings.last_frame.val
        nloop = self.settings.loop_number.val
        nrep = self.settings.repeat_each_pattern.val
        
        proj_cont = self.settings.proj_continuous.val
        
        self.vialux.set_timing(Tpic, Tacq, Swidth, Sdelay, Tdelay)
        self.vialux.set_trigger()
        
        if nrep == 1:
            self.vialux.set_sequence(fframe, lframe, nloop)
            self.vialux.run_sequence(proj_cont)
            
        elif nrep > 1:
            proj_cont = False
            for k in range(nloop):
                print("Loop", k)
                for i in range(lframe-fframe+1):
                    print("Pattern", i)
                    self.vialux.set_sequence(fframe+i, fframe+i, nrep)
                    self.vialux.run_sequence(proj_cont)
                    self.vialux.dmd.Wait()
        
            
    def generate_sequence(self):
        """
        Generation and loading of a sequence with black and white patters.
        """
        import numpy as np
        nx = self.settings.width.val
        ny = self.settings.height.val
        nz = self.pattern_num.val
        stack = np.zeros([nz,ny,nx])
        stack[0:nx-1:2,:,:] = 255
        
        self.vialux.allocate_memory(npatt = nz, bitDepth = 8)
        self.vialux.load_patterns(stack)
        self.settings['avail_memory'] = self.vialux.get_available_memory()
        self.settings['last_frame'] = nz-1
        print("Sequence generated")

    def free_sequence(self):
        self.vialux.free_sequence()
        self.settings['avail_memory'] = self.vialux.get_available_memory()
    
    def stop(self):
        self.vialux.stop()
        print('Projection Interrupted')
        
    def exit(self):
        self.vialux.close()
        print('Projection Interrupted and Memory De-allocated')
            