# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 19:20:29 2019

@author: himan
"""

import sys
import os
from moviepy.editor import VideoFileClip
from preProcessVideos import preProcess

#session_id = '123_1_1572972352'
#session_id = str(sys.argv[1])

def extractAudio(session_id):
    path = "../Sessions/" + session_id + "/session_data/subject_media/processedVideos/"
    #processedpath = "../Sessions/" + session_id + "/session_data/subject_media/processedVideos/"
    savepath = "../Sessions/" + session_id + "/session_data/subject_media/audio/"
    
    try: 
        os.mkdir(savepath) 
    except(FileExistsError): 
        pass
    
    formt = ".wav"
    filelist = os.listdir(path)
    file_count = 1
    
    for file in filelist:   
        print('Extracting audio from file '+str(file_count)+'...')
        #name = file.split('.')
        #name = name[len(name)-1]
        mp4name = file[:-4]
        video = VideoFileClip(path+file)
        audio = video.audio
        audio.write_audiofile(savepath+mp4name+formt)
        print('Finished extracting.')
        file_count += 1

if __name__ == "__main__":
    #session_id = '123_1_1572972352'
    session_id = str(sys.argv[1])
    preProcess(session_id)
    extractAudio(session_id)