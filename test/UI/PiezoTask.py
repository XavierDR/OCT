# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 10:06:00 2015

@author: oct
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 10:29:55 2015

@author: flesage

This class will take as input an image frequency and will create a task that will
generate a sine-wave to control the piezo vibrator and a digital signal
"""

from PyDAQmx import *
from PyDAQmx.DAQmxTypes import *
import numpy as np
import matplotlib.pyplot as plt

"""This class will create a sine wave of fixed amplitude and frequency (user determined)
   and generate a voltage for the piezo controller as well as two digital outputs to
   drive cameras (triggers) and image formation. Four images are used to form a single
   oct image.
   
   The module will operate independently from image acquisition.
"""

class PiezoTask():
    def __init__(self):
        
        self.ao_task = Task()
        self.camera_trig_task = Task()
        self.image_trig_task = Task()
        self.started = False
        self.samples = 512
        self.x = np.linspace(-np.pi, np.pi, self.samples)
        self.normSine = np.sin(self.x, dtype = np.float64) + 1 #Pour avoir un sinus positif
        self.frequency_hz = 10.0
        
    def setAmplitude(self, amplitude_volt):
        self.sinedata = self.normSine*amplitude_volt
        
    def setFrequency(self, frequency_hz):
        self.frequency_hz = frequency_hz
        
    def config(self):
        
        # First set sine wave with 512 points per cycle
        # Sinus wave setup
        self.ao_task.CreateAOVoltageChan("Dev1/ao1","PiezoSineWave",-10.0,10.0, DAQmx_Val_Volts,None)
        daq_freq = float(self.frequency_hz * self.samples)
        self.ao_task.CfgSampClkTiming("", daq_freq, DAQmx_Val_Rising, DAQmx_Val_ContSamps, self.samples)
        
        # Then create a pulse on the same clock
        # Sqaure wave
        camera_freq = self.frequency_hz*4;
        self.camera_trig_task.CreateCOPulseChanFreq("Dev1/ctr0",'CameraTrig',DAQmx_Val_Hz,DAQmx_Val_Low,0,camera_freq,0.5) # Pulse initialisation
        self.camera_trig_task.CfgImplicitTiming(DAQmx_Val_ContSamps,self.samples); # Clock rate
        
        # Then create a second pulse to indicate 'image' frame rate (every 4)
        # Demander a Fred
        self.image_trig_task.CreateCOPulseChanFreq("Dev1/ctr1",'ImageTrig',DAQmx_Val_Hz,DAQmx_Val_Low,0,self.frequency_hz,0.5)
        self.image_trig_task.CfgImplicitTiming(DAQmx_Val_ContSamps,self.samples);
        
        # Set triggers for synchronization
        self.camera_trig_task.CfgDigEdgeStartTrig ("/Dev1/ao/StartTrigger", DAQmx_Val_Rising);
        self.image_trig_task.CfgDigEdgeStartTrig ("/Dev1/ao/StartTrigger", DAQmx_Val_Rising);
        
        # Write data
        # Starts sine wave
        self.ao_task.WriteAnalogF64(self.samples,False,-1,DAQmx_Val_GroupByChannel, self.sinedata,None, None)
        
    def startTask(self):      
        
        if not self.started:
            self.image_trig_task.StartTask() 
            self.camera_trig_task.StartTask() # Square wave
            self.ao_task.StartTask()            #Sine wave
            self.started = True
        
    def stopTask(self):
        
        if self.started:
            self.image_trig_task.StopTask()
            self.camera_trig_task.StopTask()
            self.ao_task.StopTask()
            self.started = False

    def clearTask(self):
        
        if self.started:
            self.stopTask()
            
        self.image_trig_task.ClearTask()
        self.camera_trig_task.ClearTask()
        self.ao_task.ClearTask()
        
"""if __name__ == "__main__":
    piezo = PiezoTask()
    piezo.setAmplitude(1.0)
    piezo.setFrequency(2)
    piezo.config()
    piezo.startTask()
    
    raw_input("Running... Press enter to stop")
    
    piezo.stopTask()
    piezo.clearTask()
    plt.plot(piezo.normSine)"""