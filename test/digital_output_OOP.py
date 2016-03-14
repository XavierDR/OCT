# -*- coding: utf-8 -*-
"""
Created on Wed Aug 05 16:20:40 2015

@author: oct
"""

import PyDAQmx as Daq
import numpy as np
import time

data = np.linspace(0,10,101, dtype = Daq.uInt32)
class OutputEvents(Daq.Task):
    """ Sends out signals of events to Plexon or Blackrock so we can line up data.
    Send strobe after event code. Using both port1 and port2 to use a full 16 bits.
    """
    def __init__(self):
        Daq.Task.__init__(self)
        self.encode = np.zeros(1, dtype=np.uint32)
        self.CreateDOChan("Dev1/port1, Dev1/port2", "", Daq.DAQmx_Val_ChanForAllLines)
        #self.CfgSampClkTiming("", 10.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps , 1000)
        # Clock timing is not available on digital ports except port0

    def send_signal(self, event):
        #print event
        read = Daq.int32()
        self.encode[0] = event
        #print self.encode
        self.StartTask()
        self.WriteDigitalU32(10000, 0, 5.0, Daq.DAQmx_Val_GroupByChannel,
                             self.encode, Daq.byref(read), None)
        self.StopTask()

    def close(self):
        self.ClearTask()
        
if __name__ == "__main__":
    digital_output = OutputEvents()
    digital_output.send_signal(10)
    digital_output.close()
    
    """
    8/5/2015
    Ce code donne une onde carree de grande amplitude et de frequence d'environ
    400 Hz. Il faut trouver le moyen de controler la frequence d'ecriture de la
    pin et la waveform
    """