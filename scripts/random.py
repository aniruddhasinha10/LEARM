# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 21:27:23 2020

@author: sinha
"""

from matplotlib import pyplot as plt
import numpy as np

def f(x):
    if (x < 1):  return 1
    else:   return f(x-1) + g(x)

def g(x):
    if (x < 2): 
        return 1
    else:   
        return f(x-1) + g(x/2)


vals = np.arange(0, 15, 1)
y = []

for i in vals:
    temp = f(i)
    print (i, temp)
    y.append(temp)
    
#
plt.figure()
plt.plot(vals, y)
plt.show()

    