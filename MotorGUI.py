# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 14:22:16 2015

@author: Xavier Ducharme Rivard

This class represents a GUI for 3 axis motors control. All motors
can move individually from one another using buttons, with user-chosen
incremental steps. A starting point and an ending point can be chosen from the
GUI to decide when the imaging on the sample starts and ends.
"""

import sys, os;
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
import numpy as np

from PyQt4.QtGui import *
import subprocess
import Motors

class MotorGUI(QtGui.QMainWindow):
    
    # Constructor
    def __init__(self):
        
        super(MotorGUI, self).__init__()
        self.topLeft = [0, 0]
        self.botRight = [0, 0]
        self.initUI()           # Initialization of the GUI
    
    """ Validates correct entries of the step line edits for input >=0, otherwise
        it print an error message in the status bar
     """
    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            self.statusBar().showMessage('')
        if sender.text() == '0' or sender.text()=='-':
            self.statusBar().showMessage('Step value has to be higher than 0')
        
    # Event when the interface window is closed. This functions closes
    # the various serial ports
    def closeEvent(self, evnt):
        print('Clearing serial ports...')
        try:
            zaberMotors.ser.close()
        except NameError:
            print('No serial port to close')
        zMotor.cleanUpAPT()
        self.close()
        
    """ This function return a 2D vector containing all the matrix positions
        from the top left to the bottom right corner. The positions are in 
        micrometers
    """        
    def getMosaicVector(self):
        xSize = float(self.imgSizeXEdit.text())
        print(xSize)
        ySize = float(self.imgSizeYEdit.text())
        print(ySize)
        overlayPct = float(self.overlayEdit.text())/100
        print(overlayPct)
#        if self.topLeft == [0, 0]:
#           print('The starting point was not defined') 
#           return
        if self.botRight == [0, 0]:
            print('The ending point was not defined')
            return
        
        xRange = abs(self.topLeft[0] - self.botRight[0])
        yRange = abs(self.topLeft[1] - self.botRight[1])
        deltaX = xSize*(1 - overlayPct)
        deltaY = ySize*(1 - overlayPct)
        numDeltaX = xRange/deltaX + 1
        numDeltaY = yRange/deltaY + 1
        print('numDeltaX: ' + str(numDeltaX))
        print('numDeltaY: ' + str(numDeltaY))
        
        posx = np.zeros(numDeltaX)
        posx[0] = self.topLeft[0]
        for i in range(1, int(numDeltaX)):
            posx[i] = posx[i-1] + deltaX
            
#        print('posx')
#        print(posx)
#        i = 0
        posy = np.zeros(numDeltaY)
        posy[0] = self.topLeft[1]
        for i in range(1, int(numDeltaY)):
            posy[i] =  posy[i-1] + deltaY
#        print('posy')
#        print(posy)
        pos = []
        for j in range(len(posx)):
            for k in range(len(posy)):
                pos.append([posx[j], posy[k]])
                i += 1
#        print('Pos')
#        print(pos)
        
#        for i in range(len(pos)):
#            self.move(pos[i])
        return pos
        
        
    """ Sets the top left and botton right class parameters. These will eventually
        be used to go though the whole sample to collect a matric of
        partially overlapping images
    """
    def getMotorsPos(self):
        if self.sender() is self.topLeftBtn:
            self.topLeft = zaberMotors.getPos()
            self.topLeft[0] = float(self.topLeft[0])/2
            self.topLeft[1] = float(self.topLeft[1])/2
            print(self.topLeft)
        elif self.sender() is self.botDownBtn:
            self.botRight = zaberMotors.getPos()
            self.botRight[0] = float(self.botRight[0])/2
            self.botRight[1] = float(self.botRight[1])/2
            print(self.botRight)
    
    """ GUI initialisation """
    def initUI(self):
        
        self.statusBar()
                
        # Buttons
        self.xUpBtn = QtGui.QPushButton(self)  
        self.xUpBtn.setMinimumWidth(100)
        self.xUpBtn.setMaximumWidth(100)
        self.xUpBtn.setMinimumHeight(40)
        self.xUpBtn.setIcon(QtGui.QIcon('arrow-alt-right.png'))
        
        self.xDownBtn = QtGui.QPushButton(self)  
        self.xDownBtn.setMinimumWidth(100)
        self.xDownBtn.setMaximumWidth(100)
        self.xDownBtn.setMinimumHeight(40)
        self.xDownBtn.setIcon(QtGui.QIcon('arrow-alt-left.png'))
        
        self.yUpBtn = QtGui.QPushButton(self)  
        self.yUpBtn.setMinimumWidth(100)
        self.yUpBtn.setMaximumWidth(100)
        self.yUpBtn.setMinimumHeight(40)
        self.yUpBtn.setIcon(QtGui.QIcon('arrow-alt-right.png'))
        
        self.yDownBtn = QtGui.QPushButton(self)  
        self.yDownBtn.setMinimumWidth(100)
        self.yDownBtn.setMaximumWidth(40)
        self.yDownBtn.setMinimumHeight(40)
        self.yDownBtn.setIcon(QtGui.QIcon('arrow-alt-left.png'))
        
        self.zUpBtn = QtGui.QPushButton(self)  
        self.zUpBtn.setMinimumWidth(100)
        self.zUpBtn.setMaximumWidth(100)
        self.zUpBtn.setMinimumHeight(40)
        self.zUpBtn.setIcon(QtGui.QIcon('arrow-alt-up.png'))
        
        self.zDownBtn = QtGui.QPushButton(self)  
        self.zDownBtn.setMinimumWidth(100)
        self.zDownBtn.setMaximumWidth(100)
        self.zDownBtn.setMinimumHeight(40)
        self.zDownBtn.setIcon(QtGui.QIcon('arrow-alt-down.png'))
        
        self.topLeftBtn = QPushButton('Starting point', self)
        self.topLeftBtn.setMinimumSize(40, 40)
        
        self.botDownBtn = QPushButton('Ending point', self)
        self.botDownBtn.setMinimumSize(40, 40)
        
        self.mosaic = QPushButton('Mosaic',self)
        
        # Display text boxes
        self.font = QFont()
        self.font.setBold(True)
        self.xMotorDisplay = QtGui.QLabel('X :', self)
        self.xMotorDisplay.setMaximumWidth(40)
        self.xMotorDisplay.setFont(self.font)
        self.yMotorDisplay = QtGui.QLabel('Y :', self)
        self.yMotorDisplay.setMaximumWidth(40)
        self.yMotorDisplay.setFont(self.font)
        self.zMotorDisplay = QtGui.QLabel('Z :', self)
        self.zMotorDisplay.setMaximumWidth(40)
        self.zMotorDisplay.setFont(self.font)
        
        self.axisDisplay = QtGui.QLabel('Axis', self)
        self.stepDisplay = QtGui.QLabel('Step (um)', self)
        self.stepDisplay.setMaximumHeight(20)
        
        self.imgMatrixDisplay = QtGui.QLabel('Image acquisition parameters', self)
        self.imgMatrixDisplay.setMaximumHeight(20)
        
        self.imgSizeDisplay = QLabel('Image size (um):', self)
        self.imgSizeXDisplay = QLabel('x', self)
        
        self.overlayDisplay = QLabel('Overlay (%)', self)
        
        # Editable text boxes
        self.xStepEdit = QLineEdit('1', self)
        self.xStepEdit.setMaximumWidth(50)
        self.yStepEdit = QLineEdit('1', self)
        self.yStepEdit.setMaximumWidth(50)
        self.zStepEdit = QLineEdit('1', self)
        self.zStepEdit.setMaximumWidth(50)
        
        self.imgSizeXEdit = QLineEdit('600', self)
        self.imgSizeYEdit = QLineEdit('600', self)
        
        self.overlayEdit = QLineEdit('20', self)
        
        # Button callbacks
        self.xUpBtn.clicked.connect(self.moveUp)
        self.xDownBtn.clicked.connect(self.moveDown)
        self.yUpBtn.clicked.connect(self.moveUp)
        self.yDownBtn.clicked.connect(self.moveDown)
        self.zUpBtn.clicked.connect(self.moveUp)
        self.zDownBtn.clicked.connect(self.moveDown)
        self.topLeftBtn.clicked.connect(self.getMotorsPos)
        self.botDownBtn.clicked.connect(self.getMotorsPos)
        
        self.xStepEdit.textChanged.connect(self.check_state)
        self.mosaic.clicked.connect(self.getMosaicVector)
        
        # Input validator
        self.validator = QIntValidator()
        self.validator.setBottom(0)
        self.xStepEdit.setValidator(self.validator)
        self.yStepEdit.setValidator(self.validator)
        self.zStepEdit.setValidator(self.validator)
        
        # Horizontal line
        self.horLine = QFrame()
        self.horLine.setFrameStyle(QFrame.HLine)
        self.horLine.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)
        
        # Small grid for image size
        self.imgSizeGrid= QtGui.QGridLayout()
        self.imgSizeGrid.addWidget(self.imgSizeDisplay, 0, 0)
        self.imgSizeGrid.addWidget(self.imgSizeXEdit, 0, 1)
        self.imgSizeGrid.addWidget(self.imgSizeXDisplay, 0, 2)
        self.imgSizeGrid.addWidget(self.imgSizeYEdit, 0, 3)
        
        # Small overlay grid
        self.overlayGrid = QtGui.QGridLayout()
        self.overlayGrid.addWidget(self.overlayDisplay, 0, 0)
        self.overlayGrid.addWidget(self.overlayEdit, 0, 1)
        
        
        # Positioning of widgets in a grid
        widget = QWidget()
        widget.grid = QtGui.QGridLayout()
        widget.grid.addWidget(self.axisDisplay, 0, 0)  
        widget.grid.addWidget(self.stepDisplay, 0, 3) 
        
        widget.grid.addWidget(self.xMotorDisplay, 1, 0)
        widget.grid.addWidget(self.xDownBtn, 1, 1)
        widget.grid.addWidget(self.xUpBtn, 1, 2)
        widget.grid.addWidget(self.xStepEdit, 1, 3)
        
        widget.grid.addWidget(self.yMotorDisplay, 2, 0)
        widget.grid.addWidget(self.yDownBtn, 2, 1)
        widget.grid.addWidget(self.yUpBtn, 2, 2)
        widget.grid.addWidget(self.yStepEdit, 2, 3)
        
        widget.grid.addWidget(self.zMotorDisplay, 3, 0)
        widget.grid.addWidget(self.zDownBtn, 3, 1)
        widget.grid.addWidget(self.zUpBtn, 3, 2)
        widget.grid.addWidget(self.zStepEdit, 3, 3)
        
        widget.grid.addWidget(self.horLine, 4, 0, 1, 4)
        widget.grid.addWidget(self.imgMatrixDisplay, 5, 0, 1, 4)
        widget.grid.addWidget(self.topLeftBtn, 6, 0, 1, 2)
        widget.grid.addWidget(self.botDownBtn, 6, 2, 1, 2)
        
        widget.grid.addLayout(self.imgSizeGrid, 7, 0, 1, 4)
        widget.grid.addLayout(self.overlayGrid, 8, 0, 1 ,2)
        
        widget.grid.addWidget(self.mosaic, 9, 0)
        
        # Window properties
        widget.setLayout(widget.grid)
        self.setCentralWidget(widget)
        self.statusBar()
        self.setGeometry(100, 100, 350, 120)
        self.setMaximumSize(600, 300)
        self.setWindowTitle('Motor control')
        self.show()
    
    """ This function moves the x-y motors to the input position """
    def move(self, loc):
        if 0 < loc[0] < 300000 and  0 < loc[1] < 300000:
            zaberMotors.goTo(loc)
#            zaberMotors.motorx.move_abs(int(loc[0])*2)  # *2 because the positions are in um
#            zaberMotors.motory.move_abs(int(loc[1])*2)
    
    """Callback function for all 3 decrementing buttongs (x, y, z) """
    def moveDown(self):
        if self.sender() == self.xDownBtn:          # X axis movement
            step = self.xStepEdit.text()
            zaberMotors.motorx.move_rel(-2*int(step))
        elif self.sender() == self.yDownBtn:        # Y axis movement
            step = self.yStepEdit.text()
            zaberMotors.motory.move_rel(-2*int(step))
        elif self.sender() == self.zDownBtn:        # Z axis movement
            step = self.zStepEdit.text()
            dist = -0.0009989993023987 * float(step)
            if zMotor.getPos() < dist:
                zMotor.motor.mAbs(0.0)
                return
            zMotor.mRel(dist)
#        self.setMotorPos()
    
    """ Callback function for all 3 decrementing buttongs (x, y, z) """
    def moveUp(self):
        if self.sender() == self.xUpBtn:            # X axis movement
            step = self.xStepEdit.text()
            zaberMotors.motorx.move_rel(2*int(step))
        elif self.sender() == self.yUpBtn:          # Y axis movement
            step = self.yStepEdit.text()
            zaberMotors.motory.move_rel(2*int(step))
        elif self.sender() == self.zUpBtn:          # Z axis movement
            step = self.zStepEdit.text()
            dist = 0.0009989993023987 * float(step)
            zMotor.mRel(dist)
#        self.setMotorPos()
            
        
        
def main():
    global piezo
    global zMotor, zaberMotors
    zaberMotors = Motors.ZaberMotor()
    zMotor = Motors.ThorLabMotor(49853845, 43)
    zMotor.goHome()
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Motors control")
    ex = MotorGUI()

    app.exec_()
    
    
if __name__ == '__main__':
    main()