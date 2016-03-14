# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 16:31:56 2015

@author: oct
"""
import PiezoTask as pz
from PiezoTask import *

import test2
from test2 import *

def main():
    #global piezo
    piezo = pz.PiezoTask()
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    
    app.exec_()


if __name__ == '__main__':
    main()