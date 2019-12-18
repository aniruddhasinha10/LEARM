import speech_recognition as sr
import sys
import os
import shutil
from pydub import AudioSegment 
from pydub.silence import split_on_silence, detect_nonsilent 
import math
import datetime 

def main():
    r = sr.Recognizer() 
    
    session_id = str(sys.argv[1])
    #session_id = '123_1_1572972352'
    
    path = "../Sessions/" + session_id + "/session_data/subject_media/audio/"
    savePath = "../Sessions/" + session_id + "/analysis_data/"
    
    audio_list = os.listdir(path)
    
    for file in audio_list:
        print("*******************************************")
        print("Started Processing for file "+file + "...")
        audiofile = AudioSegment.from_wav(path+file) 
        print("\nRead the audio file: "+file)
        #print(audiofile.dBFS)
        silence_thresh = audiofile.dBFS - 10
        if silence_thresh > -16:
            silence_thresh = -16
        #print(silence_thresh)
        min_silence_thresh = 500
        
        if len(audiofile)<min_silence_thresh:
            min_silence_thresh = len(audiofile)/2
        
        timestamps = detect_nonsilent(audiofile, 
                                  min_silence_len=min_silence_thresh, 
                                  silence_thresh=silence_thresh)
        print("\nCalculated the nonsilent timestamps...")
        chunks = split_on_silence(audiofile, 
                                  # must be silent for at least 0.5 seconds 
                                  # or 500 ms. adjust this value based on user 
                                  # requirement. if the speaker stays silent for  
                                  # longer, increase this value. else, decrease it. 
                                  min_silence_len = min_silence_thresh, 
                                  # consider it silent if quieter than -16 dBFS 
                                  # adjust this per requirement 
                                  silence_thresh = silence_thresh)
        print("\nSplit the audio file into non-silent chunks "+str(len(chunks))+"...")
        
        try: 
            os.mkdir('../audio_chunks_transcription') 
        except(FileExistsError): 
            pass
        try: 
            os.mkdir(savePath) 
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
        
        svpath = savePath+"/"+file[:-4]+"/"+"text_transcript_subject.txt"
        logpath = savePath+"/"+file[:-4]+"/logs/"+"text_transcript_subject.log.txt"
        fh = open(svpath, "w+") 
        fg = open(logpath,"w+")
        i=0
        errorcount = 0
        chunkslen = len(chunks)
        print("Processing each chunk...")
        for indx,chunk in enumerate(chunks):
            # Create 0.5 seconds silence chunk 
            chunk_silent = AudioSegment.silent(duration = 10) 
            # add 0.5 sec silence to beginning and  
            # end of audio chunk. This is done so that 
            # it doesn't seem abruptly sliced. 
            audio_chunk = chunk_silent + chunk + chunk_silent 
            #audio_chunk.export("../audio_chunks_transcription/chunk{0}.wav".format(i), bitrate ='192k', format ="wav")
            #filename = '../audio_chunks_transcription/'+'chunk'+str(i)+'.wav'
            audio_chunk.export("../audio_chunks_transcription/chunk.wav".format(i), bitrate ='192k', format ="wav")
            filename = '../audio_chunks_transcription/chunk.wav'
            with sr.AudioFile(filename) as source: 
                try: 
                    # remove this if it is not working 
                    # correctly. 
                    #r.adjust_for_ambient_noise(source) 
                    audio_listened = r.record(source)
                    #audio_listened = r.listen(source) 
                    # try converting it to text 
                    rec = r.recognize_google(audio_listened) 
                    # write the output to the file.  
                    fh.write(str(timestamps[indx][0])+","+str(timestamps[indx][1])+","+rec+"\r")
                    fg.write("["+str(datetime.datetime.now())+"]"+" Audio chunk for "+str(timestamps[indx])+" seconds processed successfully.\r")
                    #audio = r.record(source)
                except sr.UnknownValueError:  
                    fg.write("["+str(datetime.datetime.now())+"]"+" Google Speech Recognition could not understand audio at "+str(timestamps[indx])+"\r")
                    fh.write(str(timestamps[indx][0])+","+str(timestamps[indx][1])+","+" "+"\r") 
                    errorcount +=1
                except sr.RequestError as e: 
                    fg.write("["+str(datetime.datetime.now())+"]"+" Could not request results from Google Speech Recognition service at "+str(timestamps[indx])+";{0}".format(e)+"\r")
                    fh.write(str(timestamps[indx][0])+","+str(timestamps[indx][1])+","+" "+"\r")
                    errorcount +=1
                except Exception as e:
                    fg.write("["+str(datetime.datetime.now())+"]"+" Exception at "+str(timestamps[indx])+":"+str(e))
                    fh.write(str(timestamps[indx][0])+","+str(timestamps[indx][1])+","+" "+"\r")
                    errorcount +=1
            sys.stdout.write('\r')
            j = (indx+1)/chunkslen
            # the exact output you're looking for:
            sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100*j))
            sys.stdout.flush()
            #sleep(0.25)
            i+=1
        fh.close()
        fg.close()
        shutil.rmtree('../audio_chunks_transcription')
        print("\nFinished Processing the file...")
        #print("\nThe file was split into " + str(chunkslen) + " chunks and processed individually, out of which " + str(errorcount) + " coudn't be processed by google")
        
if __name__ == "__main__":
    main()