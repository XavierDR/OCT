# -*- coding: utf-8 -*-
"""
Created on Wed Aug 05 14:52:04 2015

@author: oct
"""

import PyDAQmx as pydaq
from PyDAQmx import *
import numpy as np
import matplotlib.pyplot as plt
from numpy import ones, zeros


digital_output = Task()
read = int32()
written = pydaq.uInt32()

samples = 20000
sampleRate = float(samples*10)
AOFreq = 1000  # Frequency in Hz
x = numpy.linspace(0, numpy.pi, samples, dtype=np.float64)
data = numpy.sin((AOFreq/5)*x, dtype = np.float64)
digitalData = np.linspace(0,10,1000, dtype = pydaq.uInt32)

digital_output.CreateDOChan("/Dev1/PFI0", "TriggerPin", DAQmx_Val_ChanPerLine)
#digital_output.CfgSampClkTiming("", sampleRate,DAQmx_Val_Rising,DAQmx_Val_ContSamps, 1000)
#digital_output.CfgDigEdgeStartTrig("",DAQmx_Val_Rising)
digital_output.StartTask()


digital_output.WriteDigitalU32(samples, True, 10.0, DAQmx_Val_GroupByChannel, digitalData, None, None) 


digital_output.StopTask()
digital_output.ClearTask()