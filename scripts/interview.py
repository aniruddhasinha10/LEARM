# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 16:08:26 2020

@author: sinha
"""


new_random_list = [431, 12, 1, 0, -123, 431, 21, 96]
minimum = -100000
low1 = low2 = minimum

if (len(new_random_list) < 2):  
    print ("Invalid input")
    
    
for i in range(len(new_random_list)):
    if (new_random_list[i] > low1):
        low2 = low1
        low1 = new_random_list[i]
        
    elif (new_random_list[i] != low1 and low2 < new_random_list[i]):
        low2 = new_random_list[i]
        

if (low2 == minimum):
    print ("No second largest in this list")
else:
    print ("Second largest value in list is", low2)
    print ("Largest", low1)