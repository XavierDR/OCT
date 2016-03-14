# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 16:15:06 2015

@author: oct
"""




from PyDAQmx import *
import numpy as numpy
import matplotlib.pyplot as plt
from numpy import ones, zeros

analog_output = Task()
digital_output = Task()
read = int32()
written = int32()

# Frequency adjustments
samples = 20000
sampleRate = float(samples*10)
AOFreq = 1000  # Frequency in Hz
x = numpy.linspace(0, numpy.pi, samples, dtype=numpy.float64)
data = numpy.sin((AOFreq/5)*x, dtype = numpy.float64)
digitalData = ones(1000, dtype = numpy.uint32)


#data = numpy.zeros((1000), dtype=numpy.float64)
    
# DAQmx Configure Code
analog_output.CreateAOVoltageChan("Dev1/ao1","PiezoVoltage",-10.0,10.0,DAQmx_Val_Volts,None)
digital_output.CreateDOChan("/Dev1/PFI0", "TriggerPin", DAQmx_Val_ChanPerLine)
analog_output.CfgSampClkTiming("/Dev1/PFI0",sampleRate,DAQmx_Val_Rising,DAQmx_Val_ContSamps,1000)
#digital_output.CfgDigEdgeStartTrig("/Dev1/a01",DAQmx_Val_Rising)
#analog_output.RegisterDoneEvent(0,DoneCallback,NULL)
analog_output.WriteAnalogF64(samples,0,10.0,DAQmx_Val_GroupByChannel,data,None,None
)
digital_output.WriteDigitalU32(samples, True, 10.0, DAQmx_Val_GroupByChannel, digitalData, None, None) 

# DAQmx Start Code
analog_output.StartTask()
digital_output.StartTask()
#raw_input('Generating samples continuously. Press Enter to interrupt\n')
raw_input("Frequency = : %s Hz \n Press enter to interrupt" %AOFreq)

analog_output.StopTask()
analog_output.ClearTask()
#plt.plot(data)