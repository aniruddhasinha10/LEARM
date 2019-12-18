import numpy as np
import cv2
from keras.preprocessing import image
from keras.models import model_from_json
import os
import datetime
import sys

def main():    
    
    #session_id = '123_1_1572972352'
    session_id = str(sys.argv[1])
    
    haarcascade = "haarcascade_frontalface_default.xml"
    model_json = "facial_expression_model_structure.json"
    facial_rec_weights = "facial_expression_model_weights.h5"

    #-----------File locations-----------#
    videopath = "../Sessions/" + session_id + "/session_data/subject_media/processedVideos/"
    modelPath = '../Models/Video/'
    savePath = "../Sessions/" + session_id + "/analysis_data/"
    analysis_filename = "video_analysis_subject.txt"
    log_filename = "audio_analysis_subject.log.txt"
    
    #--------Initial Loads----------#
    face_cascade = cv2.CascadeClassifier(modelPath + haarcascade)
    model = model_from_json(open(modelPath + model_json, "r").read())
    model.load_weights(modelPath + facial_rec_weights) #load weights
    #--------Initial Loads Done----------#
    
    #--------------Iterate over all session videos------------------#
    filelist = os.listdir(videopath)
    file_counter = 0
    for file in filelist:
        file_counter+=1
        save_path = savePath+file[:-4]+"/"+ analysis_filename
        log_path = savePath+file[:-4]+"/"+ "logs/"+log_filename
        try: 
            os.mkdir(savePath+file[:-4]) 
        except(FileExistsError): 
            pass
        try: 
            os.mkdir(savePath+file[:-4]+"/logs") 
        except(FileExistsError): 
            pass
        save_file = open(save_path,"w+")
        log_file = open(log_path,"w+")
        cap = cv2.VideoCapture(videopath+file)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        print("*******************************************")
        print("Started Processing for file "+file + "..." + str(file_counter) + "/" + str(len(filelist)) + "\n")
        count= 1
        flag = 1
        avg = 0
        temp = 0
        frame_count = 0
        try:
            ret,img = cap.read()
            perc_frames = 1
            while(ret):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x,y,w,h) in faces:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2) #draw rectangle to main image
                    detected_face = img[int(y):int(y+h), int(x):int(x+w)] #crop detected face
                    detected_face = cv2.cvtColor(detected_face, cv2.COLOR_BGR2GRAY) #transform to gray scale
                    detected_face = cv2.resize(detected_face, (48, 48)) #resize to 48x48
                    img_pixels = image.img_to_array(detected_face)
                    img_pixels = np.expand_dims(img_pixels, axis = 0)
                    img_pixels /= 255 #pixels are in scale of [0, 255]. normalize all pixels in scale of [0, 1]
                    predictions = model.predict(img_pixels) #store probabilities of 7 expressions
                    preds = predictions[0][3] + predictions[0][5]
                    if(preds < 0.0001):
                        preds = str(0.0001)
                    else:
                        preds = str(preds)
                    t = cap.get(cv2.CAP_PROP_POS_MSEC)/1000
                    if(t < count):
                        avg+=float(preds[:5])
                        frame_count+=1
                    elif(t >= count):
                        flag = 1
                        count+=1
                        temp = avg/frame_count
                        if temp < 0.0001:
                            temp = 0.0000
                        frame_count = 0
                        avg = float(preds[:5])
                    
                    if flag:        
                        save_file.write(str((count-1)*1000)+","+str(count*1000)+","+str(temp)[:5] + "\n")
                        flag = 0
                #--------------Display Video----------------#
                #---------Display video feed ----------------#
                #cv2.putText(img, str(t), (int(x), int(y)), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.9, (255,255,255), 2)		
                #cv2.putText(img, str(float(preds[:5])*100)[:5]+'% Happy', (int(x), int(y+h)), cv2.FONT_HERSHEY_PLAIN, 0.9, (255,255,255), 1)
                #--------------------------------------------#
                #cv2.imshow('img',img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'): #press q to quit
                    save_file.close()
                    break
                #--------------------------------------------#
                sys.stdout.write("\r" + "File processing: " + str(int(100*perc_frames/total_frames)) + "%")
                sys.stdout.flush()
                perc_frames += 1
                ret, img = cap.read()
            #kill open cv things	
            save_file.close()
            cap.release()
            #cv2.destroyAllWindows()
        except Exception as e:
            log_file.write("["+str(datetime.datetime.now())+"]"+" Exception at "+str(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)[:4]+" seconds:"+str(e)+"\r")
        #----------------------------------------------------------#
    print("\nFinished processing all files for session: " + session_id)
            
if __name__ == "__main__":
    main()
