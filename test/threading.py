# -*- coding: utf-8 -*-
"""
Created on Wed Aug 05 10:31:45 2015

@author: oct
"""

import threading
import numpy

def testThread(id, message):
    print("This is a test thread!: %s %s"  %id)
    return
    
if __name__ == '__main__':
    message = "Hello!"
    for i in xrange(4):    
        t1 = threading.Thread(target = testThread, args=(i,message))
        t1.start()