import librosa
import keras
import os
import pandas as pd
import numpy as np
import sys
from pydub import AudioSegment 
import math
import datetime
import shutil

def getEmotionFeatures(file,duration):
    X, sample_rate = librosa.load(file, res_type='kaiser_fast',duration=duration,sr=22050*2,offset=0.5)
    sample_rate = np.array(sample_rate)
    result=np.array([])
    stft=np.abs(librosa.stft(X))
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate,n_mfcc=40),axis=0)
    result=np.hstack((result, mfccs))
    chroma=np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
    result=np.hstack((result, chroma))
    mel=np.mean(librosa.feature.melspectrogram(X, sr=sample_rate).T,axis=0)
    result=np.hstack((result, mel))
    feature = result
    return feature

def loadModel(path):
    from keras.models import model_from_json
    json_file = open(path+'model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(path+"Emotion_Voice_Detection_Model.h5")
    return loaded_model

def getClass(predind):
    if(predind==0):
        return "Happy"
    elif(predind==1):
        return "Normal"
    else:
        return "Other"

def main():
    #session_id = '123_1_1572972352'
    session_id = str(sys.argv[1])
    audiopath = "../Sessions/" + session_id + "/session_data/subject_media/audio/"
    modelPath = '../Models/Audio/'
    savePath = "../Sessions/" + session_id + "/analysis_data/"
    chunkPath = '../audio_chunks_analysis'
    analysis_filename = "audio_analysis_subject.txt"
    log_filename = "audio_analysis_subject.log.txt"
    
    filelist = os.listdir(audiopath)
    sample_duration = 2
    split_thresh = sample_duration*1000
    
    for file in filelist:
        print("*******************************************")
        print("Started Processing for file "+file + "...")
        audiofile = AudioSegment.from_wav(audiopath+file) 
        audiolen = len(audiofile)
        chunks = []
        timestamps = []
        count = math.ceil(audiolen/split_thresh)
        start = 0
        for i in range(count):
            if i == count-1:
                chunks.append(audiofile[start:])
                timestamps.append(start)
                break
            chunks.append(audiofile[start:start+split_thresh])
            timestamps.append(start)
            start += split_thresh  
        chunkslen = len(chunks)
        
        try: 
            os.mkdir(chunkPath) 
        except(FileExistsError): 
            pass
        try: 
            os.mkdir(savePath+"/"+file[:-4]) 
        except(FileExistsError): 
            pass
        try: 
            os.mkdir(savePath+"/"+file[:-4]+"/logs") 
        except(FileExistsError): 
            pass
        
        svpath = savePath+"/"+file[:-4]+"/"+ analysis_filename
        logpath = savePath+"/"+file[:-4]+"/logs/"+ log_filename
        fh = open(svpath, "w+") 
        fg = open(logpath,"w+")
        i=0
        for indx,chunk in enumerate(chunks):
            try:
                #chunk.export(chunkPath+"/chunk{0}.wav".format(i), bitrate ='192k', format ="wav")
                #filename = chunkPath+'/chunk'+str(i)+'.wav'
                chunk.export(chunkPath+"/chunk.wav", bitrate ='192k', format ="wav")
                filename = chunkPath+'/chunk.wav'
                result = getEmotionFeatures(filename,sample_duration)
                tries = 2
                while(result.shape[0]<313 and tries > 0):
                    sample_duration +=0.2
                    result = getEmotionFeatures(filename,sample_duration)
                    tries -=1
                
                featurelive = -(result/100)
                livedf2 = featurelive
                livedf2= pd.DataFrame(data=livedf2)
                padding = pd.DataFrame([0]*(313-len(featurelive))) 
                if(livedf2.shape[0]<313):
                    livedf2 = livedf2.append(padding,ignore_index = True)
                livedf2 = livedf2.stack().to_frame().T
                twodim= np.expand_dims(livedf2, axis=2) 
                loaded_model = loadModel(modelPath)
                livepreds = loaded_model.predict(twodim, 
                                         batch_size=32, 
                                         verbose=0)
                #livepreds1=livepreds.argmax(axis=1)
                #print("Actual Class and Rating: ",getClass(livepreds1[0]),livepreds[0][livepreds1[0]]*100)
                #print("Happiness Rating: ",livepreds[0][0])
                fh.write(str(int(timestamps[indx]))+","+str(int(timestamps[indx])+1000)+","+str(livepreds[0][0])+"\r")
                fh.write(str(int(timestamps[indx])+1000)+","+str(int(timestamps[indx])+2000)+","+str(livepreds[0][0])+"\r")
                fg.write("["+str(datetime.datetime.now())+"]"+" Audio chunk at "+str(timestamps[indx])+" seconds processed successfully.\r")
            except Exception as e: 
                #print(e)
                fg.write("["+str(datetime.datetime.now())+"]"+" Exception at "+str(timestamps[indx])+" seconds:"+str(e)+"\r")
                fh.write(str(int(timestamps[indx]))+","+str(int(timestamps[indx])+1000)+","+" "+"\r") 
                fh.write(str(int(timestamps[indx])+1000)+","+str(int(timestamps[indx])+2000)+","+" "+"\r") 
            
            sys.stdout.write('\r')
            j = (indx+1)/chunkslen
            # the exact output you're looking for:
            sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
            sys.stdout.flush()
            i+=1
        fh.close()
        fg.close()
        shutil.rmtree(chunkPath)
        print("\nFinished Processing the file...")
    
if __name__ == "__main__":
    main()