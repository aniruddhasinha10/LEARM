# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 22:21:42 2019

@author: sinha
"""
import os
import sys
import pandas as pd
import numpy as np
import random
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
import re
from sklearn.externals import joblib
import datetime

'''
Preprocess the text content
'''

def preprocessInputText(data):
    data['content'] = data['content'].str.replace('[^\w\s]',' ')
    stop = stopwords.words('english')
    data['content'] = data['content'].apply(lambda x:" ".join(x for x in x.split() if x not in stop))
    
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    data['content'] = data['content'].apply(lambda x:" ".join( [lemmatizer.lemmatize(word) for word in x.split()] ))
    
    return data

'''
Load the model
'''
def loadModel(path):
    import pickle
    with open(path + 'SVM.pkl', 'rb') as file1:
        loaded_SVM_model = pickle.load(file1)
    with open(path + 'countVectors.pkl', 'rb') as file2:
        count_vectors = pickle.load(file2)
    
    return loaded_SVM_model, count_vectors

def convertOutputDataframe(input_data, happiness_ratings):
    output_dict = {'start':input_data['Start_Time'], 'end':input_data['End_Time'], 'rating':happiness_ratings}
    output_df = pd.DataFrame(output_dict)
    return output_df

def getEmptyCuesRows(data):
    empty_text = ' '
    index_list = []
    for i in range(len(data['content'])):
        if data['content'][i] == empty_text:
            index_list.append(i)
    
    return index_list
   
def setOutputEmptyRows(ratings, empty_rows):
    for i in empty_rows:
        ratings[i] = 0
    
    return ratings

def getClass(predicted):
    emotions = []
    for item in predicted:
        if item == 0:
            emotions.append("Happy")
        elif item == 1:
            emotions.append("Other")
        else:
            emotions.append("Sad")
    
    return emotions


'''
----------------------------------------------
----------------------------------------------
----------------------------------------------
----------------------------------------------

Reading the transcripted text files

----------------------------------------------
----------------------------------------------
----------------------------------------------
----------------------------------------------
'''
def main():
    #session_id = '123_1_1572972352'
    session_id = str(sys.argv[1])
#    textpath = "../Sessions/" + session_id + "/session_data/subject_media/audio/"
    modelPath = '../Models/Text/'
    savePath = "../Sessions/" + session_id + "/analysis_data/"
    analysis_filename = "text_transcript_subject.txt"
    output_filename = "text_analysis_subject.txt"
    log_filename = "text_analysis_subject.log.txt"
    
    # Load the models
    loaded_SVM_model, count_vectors = loadModel(modelPath)
    
    for subdir, dirs, files in os.walk(savePath):
        for file in files:
            if file == analysis_filename:
                try: 
                    os.mkdir(subdir + "/logs") 
                except(FileExistsError): 
                    pass
                
                logpath = subdir + "/logs/" + log_filename
                fg = open(logpath,"w+")
                
                try:
                    curr_path = subdir + '/' + analysis_filename
                    print("*******************************************")
                    print("\nStarted Text Emotion Processing for file "+ os.path.split(subdir)[1] + '/' + file + "...\n")
                    input_data = pd.read_csv(curr_path, sep=',', header = None)
                    input_data.columns = ['Start_Time', 'End_Time', 'content']
                    empty_cues_rows = getEmptyCuesRows(input_data)
                    
                    input_data = preprocessInputText(input_data)
                    
                    # Extract count vectors features from the text content
                    text_count = count_vectors.transform(input_data['content'])
                    
                    #Predict emotion of the text using LSVM
                    text_pred = loaded_SVM_model.predict(text_count)
                    emotions = getClass(text_pred)
                    
                    # Get the predicted probabilities of each emotion
                    text_pred_prob = loaded_SVM_model.predict_proba(text_count)
                    
                    # Get the happiness ratings from the first column of the predicted probabilities,
                    # multiply it by 100 to get the percentage value and
                    happiness_ratings = np.multiply(text_pred_prob[:,0],100)
                    happiness_ratings = setOutputEmptyRows(happiness_ratings, empty_cues_rows)
                    
                    output_file = convertOutputDataframe(input_data, happiness_ratings)
                    output_path = subdir + '/' + output_filename
                    output_file.to_csv(output_path, header=None, index=None, sep=',')
                    print("\nFinished Processing the file...")
                    fg.write("["+str(datetime.datetime.now())+"]"+" Transcript text analyzed successfully.\r")
                except Exception as e: 
                #print(e)
                    fg.write("["+str(datetime.datetime.now())+"]"+" Exception raised: "+str(e)+"\r")
                
                fg.close()

if __name__ == "__main__":
    main()