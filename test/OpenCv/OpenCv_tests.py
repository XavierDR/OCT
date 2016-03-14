# -*- coding: utf-8 -*-
"""
Created on Fri Aug 07 14:35:58 2015

@author: oct
"""

import sys
import numpy as np
import cv2 as cv2
from matplotlib import pyplot as plt


desert = cv2.imread('Desert.jpg', cv2.IMREAD_COLOR)
cv2.imshow("Le desert!", desert)
cv2.waitKey(0)
cv2.destroyAllWindows()

b, g, r = cv2.split(desert)
desert2 = cv2.merge([r,g,b])

plt.imshow(desert2, cmap = 'gray')