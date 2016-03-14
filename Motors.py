# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 14:13:00 2015

@author: Xavier Ducharme Rivard

This module defines two different motor usage classes:
ThorLabs LabJack motor
Zaber T-LSR series
"""

import binary
import APTMotor
import time
import serial
from serial import SerialException

""" This class holds the code to initialize and use a ThorLabs LabJack motor.
 Plenty more methods of moving the motor and getting information are available
 when using the APTMotor instance directly.  """
class ThorLabMotor(APTMotor.APTMotor):
    def __init__(self, SN, HWTYPE):
        super(ThorLabMotor, self).__init__(SN, HWTYPE)
#        self.motor =  APTMotor.APTMotor(SN, HWTYPE) # SN and motor type
#        self.motor.initializeHardwareDevice()
        self.initializeHardwareDevice()
       
    def goHome(self):
        self.mAbs(1.0)
        
        
""" This class contains all the linear Zaber connected in series. If there are
 more or less motors than presently (x and y), it is simply possible to 
 add them to the class attributes as a new BinaryDevice instance. 
 https://www.zaber.com/products/product_detail.php?detail=T-LSR150B """
class ZaberMotor():
    def __init__(self):
        try:
            self.ser = binary.BinarySerial('COM3')
            self.motorx = binary.BinaryDevice(self.ser, 1)
            self.motory = binary.BinaryDevice(self.ser, 2)
            self.goHome()
        except SerialException:
            print('Port already open, motor instances not created')
            
        self.range = [0, 300000]
            
    def getPos(self):
        pos = [0, 0]
        pos[0] = self.motorx.get_pos()
        pos[1] = self.motory.get_pos()
        return pos
    
    def goHome(self):
        print('Moving motors home...')
        self.motorx.home()
        self.motory.home()
    
    """ This function moves both motors to the input position (in um) """
    def goTo(self, pos):
        self.motorx.move_abs(pos[0]*2)
        self.motory.move_abs(pos[1]*2)
        