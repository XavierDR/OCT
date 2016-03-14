# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 15:25:14 2015

@author: OCT
"""

import PiezoTask as pz
import subprocess
import socket


if __name__ == '__main__':
    piezo = pz.PiezoTask()
    p = subprocess.Popen

    TCP_IP = '132.207.157.48'
    TCP_PORT = 21000
    BUFFER_SIZE = 256  # Normally 1024, but we want fast response
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    
    conn, addr = s.accept()
    print 'Connection address:', addr
    while 1:
        fileName = conn.recv(BUFFER_SIZE)
        if not fileName: break
        print "File name acquired: ", fileName
        conn.send(fileName)  # echo
        
        # Run the executable
        args = 'C:\Users\oct\CiCLSimple.exe' + ' ' + fileName
        print 'All the arguments', args
#        p = subprocess.Popen(args, shell=False)
        
        
            
            
    conn.close()
    