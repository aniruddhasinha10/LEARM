# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 19:20:29 2019

@author: himan
"""

import sys
import os
import voiceEmotionRecognizer
import faceExpressionRecognizer
import textEmotionRecognizer

session_id = str(sys.argv[1])
analysisPath = "../Sessions/" + session_id + "/analysis_data"

try: 
    os.mkdir(analysisPath) 
except(FileExistsError): 
    pass

print("\n---------------RUNNING AUDIO ANALYSIS---------------\n")
voiceEmotionRecognizer.main()
print("\n--------------AUDIO ANALYSIS COMPLETE---------------")

print("\n---------------RUNNING VIDEO ANALYSIS---------------\n")
faceExpressionRecognizer.main()
print("\n--------------VIDEO ANALYSIS COMPLETE---------------")

print("\n---------------RUNNING TEXT ANALYSIS---------------\n")
textEmotionRecognizer.main()
print("\n--------------TEXT ANALYSIS COMPLETE---------------")