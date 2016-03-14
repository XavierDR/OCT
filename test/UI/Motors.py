# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 14:13:00 2015

@author: OCT
"""

import binary
import APTMotor
import time
import serial
from serial import SerialException

def main():
    # ThorLabs APT Motor
    print('Hey')
    Motor1 = APTMotor.APTMotor(49853845, HWTYPE = 43)
    print('Hey')
    Motor1.initializeHardwareDevice()
    print(Motor1.getPos())
    Motor1.mRel(1)
    Motor1.mRel(-1)
    Motor1.cleanUpAPT()
#    
    # Zaber motor 1
    ser = binary.BinarySerial('COM4')
    Motor2 = binary.BinaryDevice(ser, 1)
    Motor2.move_rel(5000)
    Motor2.move_rel(-5000)
    
    # Zaber motor 2
    Motor3 = binary.BinaryDevice(ser, 2)
    Motor3.move_rel(5000)
    Motor3.move_rel(-5000)    
    
if __name__ == '__main__':
    main()
    
class ThorLabMotor():
    def __init__(self):
       self.motor =  APTMotor.APTMotor(49853845, HWTYPE = 43)
       self.motor.initializeHardwareDevice()
       self.motor.mbAbs(1.0)
       self.motor.mRel(-1.0)
       
    def moveRel(self, dist):
        self.motor.mRel(dist)
        
    def getPos(self):
        return self.motor.getPos()
        
        
# Pour bouger les motors Zaber de 1um, il faut faire 2.015748031 steps. Par contre,
# la fonction prend des int, donc on doit arrondir a 0.9921875um par step
# https://www.zaber.com/products/product_detail.php?detail=T-LSR150B
class ZaberMotor():
    def __init__(self):
        try:
            self.ser = binary.BinarySerial('COM4')
            self.motorx = binary.BinaryDevice(self.ser, 1)
            self.motory = binary.BinaryDevice(self.ser, 2)
            self.goHome()
        except SerialException:
            print('Port already open, motor instances not created')
    
    def goHome(self):
        print('Moving motors home...')
        self.motorx.home()
        self.motory.home()
        
    def getPos(self):
        pos = [0, 0]
        pos[0] = self.motorx.get_pos()
        pos[1] = self.motory.get_pos()
        return pos
        