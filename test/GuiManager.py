import sys
#import PySide as PySide  ## this will force pyqtgraph to use PySide instead of PyQt4
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from threading import Timer
import time
import Parameters
import pickle
from array import array
import struct
#import uc480
import datetime
import scipy.io as sio
import os
import math
import Parameters
from AcquisitionWorker import AcquisitionWorker
import Queue
#import sched
          
class GuiManager(QtGui.QMainWindow):
    
    def __init__(self):
        super(GuiManager, self).__init__()
        self.createLayout()
        
    def closeEvent(self, event):
        print 'User asked to close the app'
        self.stopAcquisition()
        Parameters.isAppKilled = True
        #time.sleep(0.1) #Wait for the worker death
        event.accept() # let the window close         
    
    def startAcquisition(self):
        if Parameters.isConnected == False:
            return
        Parameters.isSaving = Parameters.paramObject.child("Saving parameters", "saveResults").value()
        if Parameters.isSaving == True:
            theDate = datetime.datetime.today() .strftime('%Y%m%d')   
            theTime = datetime.datetime.today() .strftime('%H%M%S')   
            theName=Parameters.paramObject.child("Saving parameters", "Experiment name").value()
            #Check counter increment
            folderParent = 'C:/InterferometryResults/' + theDate
            counter = 1
            folderFound = False
            theFolder = folderParent + '/' + theName + '_' + str(counter).zfill(3)
            if not os.path.exists(folderParent): #Make sure parent exist
                os.makedirs(folderParent)                
            while folderFound == False and counter < 1000: #Loop until folder is found
                if not os.path.exists(theFolder): #Make sure parent exist
                    os.makedirs(theFolder)        
                    folderFound = True
                else:
                    counter = counter + 1
                    theFolder = folderParent + '/' + theName + '_' + str(counter).zfill(3)
            if counter < 1000:
                Parameters.savingFolder = theFolder
                if not os.path.exists(theFolder):
                    os.makedirs(theFolder)               
            else:
                Parameters.isSaving = False; #Should not happen.
        self.btStart.setEnabled(False)
        self.btStop.setEnabled(True)
        self.btOpen.setEnabled(False)
        #Get the parameter values
        Parameters.nSamples=Parameters.paramObject.child("Acquisition Parameters", "Number of samples to acquire").value()
        acqMode=Parameters.paramObject.child("Trigger Options", "Acquisition mode").value()
        triggerAmplitude=Parameters.paramObject.child("Trigger Options", "Trigger amplitude").value()
        motorSpeed=Parameters.paramObject.child("Acquisition Parameters", "Rotation speed (%)").value()+28 #28 is calibration
        nBlocks=int(math.ceil(float(Parameters.nSamples)/512)) #Must be a multiple of 512
        Parameters.nSamples = nBlocks*512
        Parameters.paramObject.child("Acquisition Parameters", "Number of samples to acquire").setValue(Parameters.nSamples)

        #Set frequency in free mode. These settings could be optimized depending on the computer.
        freq=2500000 #10im/s
        if Parameters.nSamples > 100352:
            freq=5000000 #5im/s
        if Parameters.nSamples > 300032:
            freq=12500000 #2im/s               
        if Parameters.nSamples > 1000000:
            freq=25000000 #1im/s     
        if Parameters.nSamples > 2000000:
            freq=50000000 #0.5im/s               
        
        #Start the acquisition on the FPGA
        data = []
        data = array('i')
        data.append(1)
        data.append(freq)
        data.append(2)
        data.append(acqMode)
        data.append(3)
        data.append(nBlocks)
        data.append(4)
        data.append(motorSpeed)
        data.append(5)
        data.append(triggerAmplitude)
        data.append(6)
        data.append(0)
        
        theBytes = struct.pack('i' * len(data), *data)
        buf = bytearray(theBytes)
        Parameters.dev.WriteToPipeIn(128, buf)
    
        Parameters.dev.SetWireInValue(0, 1+2+8, 1+2+8);Parameters.dev.UpdateWireIns() #Enable DDR2 reading and writing and activate memory.
        time.sleep(0.1); #Wait to make sure everything is ready. TODO: Reduce this.
        Parameters.dev.SetWireInValue(0, 4, 4);Parameters.dev.UpdateWireIns() #Start acquisition clock.
        
        #self.plotTr.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted
        Parameters.theQueue = Queue.Queue() #Create the queue
        #self.DisplayUpdater(0)
        self.workThread.start(); #Start the display worker

    
    def stopAcquisition(self):
        print 'Stopping...'
        if hasattr(self,'tDisplay'):
            self.tDisplay.cancel()        
        self.workThread.exitWorker();
        while self.workThread.isRunning == True:
            time.sleep(0.01) #Wait for the worker death, before resetting the board
        Parameters.dev.SetWireInValue(0, 0, 1+2+4+8);Parameters.dev.UpdateWireIns() #Reset board.

        #Save format: Results / YYMMDD / ExperimentName_Counter. Could also use the time.
        if Parameters.isSaving == True:  
            #global state
            state = Parameters.paramObject.saveState()
            file = open(Parameters.savingFolder + '\Parameters.txt', 'w')
            pickle.dump(state, file)
            file.close()            
        print 'Stopped.'
        self.btStart.setEnabled(True)
        self.btStop.setEnabled(False)
        self.btOpen.setEnabled(True)
    '''
    def DisplayUpdater(self,dummy):
        if Parameters.isAppKilled == True:
            return;   
        if Parameters.theQueue.empty():
            print 'no data...'
        while not Parameters.theQueue.empty(): #Empty the display queue
            data = Parameters.theQueue.get()
            #print 'data available!' 
        if 'data' in locals():
            #print 'display data' + str(data[2])
            self.setDataCurveTr(data)
        tDisplay = Timer(2, self.DisplayUpdater, [0],{})
        tDisplay.start()          
    '''   
    def motorSpeedChanged(self,value):
        newSpeed=Parameters.paramObject.child("Acquisition Parameters", "Rotation speed (%)").value()
        newSpeed=newSpeed+28 #Calibration
        
        #Debug
        #Parameters.paramObject.child("Acquisition Parameters", "Rotation speed (%)").setOpts(enabled=False)
        #Parameters.paramObject.child("Acquisition Parameters", "Rotation speed (%)").setOpts(visible=False)
        #Parameters.paramObject.child("Acquisition Parameters", "Rotation speed (%)").setOpts(value=200)

        data = []
        data = array('i')
        data.append(4)
        data.append(newSpeed)
        data.append(0) #Minimum size is 8 'int'
        data.append(0)        
        data.append(0)
        data.append(0)        
        data.append(0)
        data.append(0)                    
        
        theBytes = struct.pack('i' * len(data), *data)
        Parameters.bufferToDev = bytearray(theBytes)
        Parameters.bufferToDevReady = True
        
        
    def triggerChanged(self,value):
        acqMode=Parameters.paramObject.child("Trigger Options", "Acquisition mode").value()
        triggerAmplitude=Parameters.paramObject.child("Trigger Options", "Trigger amplitude").value()

        data = []
        data = array('i')
        data.append(2)
        data.append(acqMode)
        data.append(5)
        data.append(triggerAmplitude)
        data.append(0)
        data.append(0)
        data.append(0)
        data.append(0)        
        
        theBytes = struct.pack('i' * len(data), *data)
        print str(theBytes)
        
        Parameters.bufferToDev = bytearray(theBytes)
        Parameters.bufferToDevReady = True     
        
    def triggerHalfSwitch(self):
        Parameters.triggerToDev = True
        
    def saveParam(self):
        #global state
        state = Parameters.paramObject.saveState()
        file = open('dump.txt', 'w')
        pickle.dump(state, file)
        file.close()
        
    def restoreParam(self):
        #lobal state
        file = open('dump.txt', 'r')
        state = pickle.load(file)
        #add = Parameters.paramObject['Save/Restore functionality', 'Restore State', 'Add missing items']
        #rem = Parameters.paramObject['Save/Restore functionality', 'Restore State', 'Remove extra items']
        Parameters.paramObject.restoreState(state, addChildren=False, removeChildren=False)           
    
    #Set the status text (system connected or not)
    def setStatus(self, isConnected, isError = False):
        def dotChange(item, nDots): #Timer function to display a varying number of dots after "retrying"
            if Parameters.isConnected == True:
                return;
            if Parameters.isAppKilled == True:
                return;                   
            textNotConnected = "System not connected, retrying"
            item.setText(textNotConnected+".")
            #Number of dots varies from 1 to 5
            if nDots == 1:
                textDots = "."
                nDots = 2
            elif nDots == 2:
                textDots = ".."
                nDots = 3
            elif nDots == 3:
                textDots = "..."
                nDots = 4
            elif nDots == 4:
                textDots = "...."
                nDots = 5        
            else:
                textDots = "....."
                nDots = 1    
            item.setForeground(QtGui.QColor("red"))
            item.setText(textNotConnected+textDots)
            self.timerDotChange = Timer(0.25, dotChange, [self.itemStatus, nDots])
            self.timerDotChange.start()          
        if (isError == True): #System not connected    
            print "Error"
            if hasattr(self,'timerDotChange'):
                self.timerDotChange.cancel()
                time.sleep(0.5)
            self.itemStatus.setForeground(QtGui.QColor("red"))                
            self.itemStatus.setText("Error with system. Please restart the application and the system.")              
        elif (isConnected == False): #System not connected      
            nDots = 1
            if hasattr(self,'timerDotChange'):
                self.timerDotChange.cancel()            
            self.timerDotChange = Timer(0.25, dotChange, [self.itemStatus, nDots])
            self.timerDotChange.start()              
        else:    
            print "Connected"
            if hasattr(self,'timerDotChange'):
                self.timerDotChange.cancel()
                time.sleep(0.1)
            self.itemStatus.setForeground(QtGui.QColor("green"))                
            self.itemStatus.setText("System connected.")
            print "Connected2"

    #Set the status text (system connected or not)
    def setCameraStatus(self, isConnected):
        def dotChange(item, nDots): #Timer function to display a varying number of dots after "retrying"
            if Parameters.isCameraConnected == True:
                return;
            if Parameters.isAppKilled == True:
                return;                
            textNotConnected = "Camera not connected, retrying"
            item.setText(textNotConnected+".")
            #Number of dots varies from 1 to 5
            if nDots == 1:
                textDots = "."
                nDots = 2
            elif nDots == 2:
                textDots = ".."
                nDots = 3
            elif nDots == 3:
                textDots = "..."
                nDots = 4
            elif nDots == 4:
                textDots = "...."
                nDots = 5        
            else:
                textDots = "....."
                nDots = 1    
            item.setForeground(QtGui.QColor("red"))
            item.setText(textNotConnected+textDots)
            self.timerDotChangeCamera = Timer(0.25, dotChange, [self.itemCameraStatus, nDots])
            self.timerDotChangeCamera.start()                      
        if (isConnected == False): #System not connected     
            print 'cam oups'
            nDots = 1
            if hasattr(self,'timerDotChangeCamera'):
                self.timerDotChangeCamera.cancel()            
            self.timerDotChangeCamera = Timer(0.25, dotChange, [self.itemCameraStatus, nDots])
            self.timerDotChangeCamera.start()              
        else:    
            print "Camera connected"
            if hasattr(self,'timerDotChangeCamera'):
                self.timerDotChangeCamera.cancel()
                time.sleep(0.1)
            self.itemCameraStatus.setForeground(QtGui.QColor("green"))                
            self.itemCameraStatus.setText("Camera connected.")
            print "Camera connected2"
            
    #Set the status text (system connected or not)
    def setInfo(self, text):
        self.tbInfo.append(text)
            
    #Set the status text (system connected or not)
    def setWire(self, mem1, mem2, mem3, mem4, maxValPos):
        self.itemMemory.setText("Acquisition board memory usage:\nDDR2: " + str(mem1) + " bytes.\nFIFO in: " + str(mem2) + " bytes.\nFIFO out: " + str(mem3) + " bytes.\nFIFO out (minimum): " + str(mem4) + " bytes.")
        self.itemMaxValPos.setText("Maximum RF value position: " + str(maxValPos))
                
    def createLayout(self):
        print 'Creating layout...'
        self.setWindowTitle('Interferometry Acquisition GUI')  
        #self.widget = QtGui.QWidget()
        #self.setCentralWidget(self.widget)
        self.layout = pg.LayoutWidget()
        #self.widget.setLayout(self.layout)
        self.setCentralWidget(self.layout)
        
        #Create GUI
        sizePolicyBt = QtGui.QSizePolicy(1, 1)
        sizePolicyBt.setHorizontalStretch(0)
        sizePolicyBt.setVerticalStretch(0)
        
        self.btOpen = QtGui.QPushButton("Open\nprevious results")
        sizePolicyBt.setHeightForWidth(self.btOpen.sizePolicy().hasHeightForWidth())
        self.btOpen.setSizePolicy(sizePolicyBt);
        self.btOpen.setStyleSheet("background-color: yellow; font-size: 16px; font: bold")
        
        self.btStart = QtGui.QPushButton("Start\nacquisition")
        sizePolicyBt.setHeightForWidth(self.btStart.sizePolicy().hasHeightForWidth())
        self.btStart.setSizePolicy(sizePolicyBt);
        self.btStart.setStyleSheet("background-color: green; font-size: 16px; font: bold")
        self.btStart.clicked.connect(self.startAcquisition)
        
        self.btStop = QtGui.QPushButton("Stop\nacquisition")
        sizePolicyBt.setHeightForWidth(self.btStop.sizePolicy().hasHeightForWidth())
        self.btStop.setSizePolicy(sizePolicyBt);
        self.btStop.setStyleSheet("background-color: red; font-size: 16px; font: bold")
        self.btStop.clicked.connect(self.stopAcquisition)
        self.btStop.setEnabled(False)
        
        self.paramTree = ParameterTree()
        self.paramTree.setParameters(Parameters.paramObject, showTop=False)
        self.paramTree.setWindowTitle('pyqtgraph example: Parameter Tree')
        self.paramTree.setMinimumWidth(350)
        self.paramTree.setMaximumWidth(350)
        sizePolicyPt = QtGui.QSizePolicy(1,1)
        sizePolicyPt.setHorizontalStretch(QtGui.QSizePolicy.Fixed)
        sizePolicyPt.setVerticalStretch(1)
        self.paramTree.setSizePolicy(sizePolicyPt);


        ## Create random 2D data
        data = np.random.normal(size=(512, 512)) + pg.gaussianFilter(np.random.normal(size=(512, 512)), (5, 5)) * 20 + 100
        data = data[:,:,np.newaxis]
        data = data.repeat(3,2)

        self.plotTl = pg.GraphicsView()
        self.plotTlImage = pg.ImageItem(data[:,:,:]) #parent=self.plotTl
        self.plotTlViewBox = pg.ViewBox()         
        self.plotTl.setCentralWidget(self.plotTlViewBox)
        self.plotTlViewBox.addItem(self.plotTlImage)

    
        self.plotTr = pg.PlotWidget(title="Interferometry", labels={'left': 'Signal amplitude (A.U.)', 'bottom': 'Distance (mm)'})
        #self.plotTlViewBox2.addItem(self.plotTr)
        self.plotTrCurve = self.plotTr.plot(pen=(255,0,0),name='C1') #Red
        self.plotTrCurve2 = self.plotTr.plot(pen=(0,255,0),name='C2') #Green
        #self.plotTlViewBox2.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted
        #self.plotTr.addLegend('Test')
        self.plotTr.setYRange(-1000, 1000)
 
        self.plotBl = pg.PlotWidget(title="Distance", labels={'left': 'Distance (mm)', 'bottom': 'Number of acquisitions'})
        
        self.plotBlCurve = self.plotBl.plot(pen=(255,0,0),name='C1')
        self.plotBl.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted       
        self.plotBl.setMaximumWidth(3500)
        
        self.tbInfo = QtGui.QTextEdit()
        self.tbInfo.setEnabled(False)
        palette = self.tbInfo.palette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor("white")) #White background
        self.tbInfo.setPalette(palette)
        self.tbInfo.setTextColor(QtGui.QColor("black"))
        self.tbInfo.insertPlainText("Useful information will appear here.")
        
        #Create list view of multiple items
        self.tbStatus = QtGui.QListView()
        self.tbStatus.setEnabled(False)
        palette = self.tbStatus.palette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor("white")) #White background
        self.tbStatus.setPalette(palette)
        itemModelStatus = QtGui.QStandardItemModel(self.tbStatus)
        self.tbStatus.setModel(itemModelStatus)
        #Add system status
        self.itemStatus = QtGui.QStandardItem()
        self.setStatus(False)      
        itemModelStatus.appendRow(self.itemStatus)    
        #Add camera status
        self.itemCameraStatus = QtGui.QStandardItem()
        self.setCameraStatus(False)      
        itemModelStatus.appendRow(self.itemCameraStatus)           
        #Add memory usage
        self.itemMemory = QtGui.QStandardItem("Acquisition board memory usage: N/A")
        self.itemMemory.setForeground(QtGui.QColor("black"))  
        itemModelStatus.appendRow(self.itemMemory)
        #Add max value position
        self.itemMaxValPos = QtGui.QStandardItem("Maximum RF value position: N/A")
        self.itemMaxValPos.setForeground(QtGui.QColor("black"))  
        itemModelStatus.appendRow(self.itemMaxValPos)        
        
        
        #layout.addWidget(QtGui.QLabel("These are two views of the same data. They should always display the same values."), 0, 0, 1, 2)
        self.layout.addWidget(self.btOpen, 9, 6, 1, 1)
        self.layout.addWidget(self.btStart, 9, 7, 1, 1)
        self.layout.addWidget(self.btStop, 9, 8, 1, 1)
        self.layout.addWidget(self.paramTree, 0, 0, 10, 3)
        self.layout.addWidget(self.plotTl, 0, 3, 5, 3) 
        self.layout.addWidget(self.plotTr, 0, 6, 5, 3)
        self.layout.addWidget(self.plotBl, 5, 3, 5, 3)
        self.layout.addWidget(self.tbInfo, 5, 6, 2, 3)
        self.layout.addWidget(self.tbStatus, 7, 6, 2, 3)

        self.layout.layout.setColumnStretch(3,1)
        self.layout.layout.setColumnStretch(4,1)
        self.layout.layout.setColumnStretch(5,1)
        self.layout.layout.setColumnStretch(6,1)
        self.layout.layout.setColumnStretch(7,1)
        self.layout.layout.setColumnStretch(8,1)

        self.show()
        self.resize(1500,800)
        self.move(100,100)    
        
        Parameters.paramObject.param('Save/Restore functionality', 'Save State').sigActivated.connect(self.saveParam)
        Parameters.paramObject.param('Save/Restore functionality', 'Restore State').sigActivated.connect(self.restoreParam)
        
        Parameters.paramObject.child("Acquisition Parameters", "Rotation speed (%)").sigValueChanged.connect(self.motorSpeedChanged)
        Parameters.paramObject.child("Trigger Options", "Acquisition mode").sigValueChanged.connect(self.triggerChanged)
        Parameters.paramObject.child("Trigger Options", "Trigger amplitude").sigValueChanged.connect(self.triggerChanged)
        Parameters.paramObject.child("Trigger Options", "Trigger switch 1/2").sigActivated.connect(self.triggerHalfSwitch)
        
        # adding by emitting signal in different thread
        self.workThread = AcquisitionWorker()
        self.workThread.updateDataCamera.connect(self.setDataCurveTl)
        self.workThread.updateDataInterf.connect(self.setDataCurveTr)
        self.workThread.updateDataDistance.connect(self.setDataCurveBl)
        self.workThread.updateDataDistance2.connect(self.setDataCurveBl2)
        self.workThread.updateWire.connect(self.setWire)
        self.workThread.setStatus.connect(self.setStatus)
        self.workThread.setInfo.connect(self.setInfo)
        self.testCount = 0;
        
        #Fill the plots with dummy data
        self.data = np.random.normal(size=(10,1000))    
        self.plotTrXAxis = np.arange(1000) * (0.01)
        self.plotBlXAxis = np.arange(1000) * (1)
        self.plotTrCurve.setData(x=self.plotTrXAxis,y=self.data[2%10],name='C1')
        self.plotTrCurve2.setData(x=self.plotTrXAxis,y=self.data[3%10],name='C2')    
        self.plotBlCurve.setData(x=self.plotBlXAxis,y=self.data[4%10],name='C1')            
        
        self.valueTest = 1
        
    def setDataCurveTl(self, data):
        self.dataImage1 = data
        self.plotTlImage.setImage(data)
        self.testCount = self.testCount + 1;
        
    def setDataCurveTr(self, dataIn):   
        self.plotTrCurve.setData(dataIn[0:len(dataIn):2],name='C1')        
        self.plotTrCurve2.setData(dataIn[1:len(dataIn):2],name='C2')    

    def setDataCurveBl(self, dataIn):
        self.plotBlCurve.setData(dataIn,name='C1')       
        
    def setDataCurveBl2(self, xIn, dataIn):
        self.plotBlCurve.setData(x=xIn,y=dataIn,name='C1')          