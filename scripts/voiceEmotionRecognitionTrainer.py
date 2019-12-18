#!/usr/bin/env python
# coding: utf-8

# In[22]:


import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from matplotlib.pyplot import specgram
import keras
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.layers import Input, Flatten, Dropout, Activation
from keras.layers import Conv1D, MaxPooling1D, AveragePooling1D
from keras.models import Model
from keras.callbacks import ModelCheckpoint
from sklearn.metrics import confusion_matrix

from keras import regularizers
import os
import pandas as pd
import glob
import scipy.io.wavfile
import numpy as np
import sys
from keras.callbacks import EarlyStopping
from playsound import playsound
from sklearn.utils import shuffle
import json

from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder


# In[ ]:


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

def getCNNModel():
    model = Sequential()
    model.add(Conv1D(256,kernel_size=5,padding='same',activation='relu',input_shape=(X_train.shape[1],1)))
    model.add(Conv1D(128,kernel_size=5,padding='same',activation='relu'))
    model.add(Dropout(0.2))
    model.add(MaxPooling1D(pool_size=(8)))
    model.add(Conv1D(128,kernel_size=5,padding='same',activation='relu'))
    model.add(Conv1D(128,kernel_size=5,padding='same',activation='relu'))
    model.add(Conv1D(128,kernel_size=5,padding='same',activation='relu'))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(3,activation='softmax'))
    opt = keras.optimizers.Adam(lr=0.0005, decay=1e-6)

    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer=opt,metrics=['accuracy'])
    
def plotTrainingLossAndAccuracy(history):
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validate'], loc='lower right')
    plt.show()

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

    print("\nCNN accuracy for training set: ",history.history['accuracy'][len(history.history['accuracy'])-1] * 100)
    print("CNN accuracy for validation set: ",history.history['val_accuracy'][len(history.history['val_accuracy'])-1] * 100)
    

def saveModel():
    


# In[3]:


np.random.seed(5)
datalist = os.listdir('data/')
type(datalist)
print(len(datalist))


# In[4]:


print(datalist[5000])


# In[5]:


print(datalist[100][18:20])


# In[6]:


data, sampling_rate = librosa.load('data/'+datalist[0])


# In[7]:


plt.figure(figsize=(15, 5))
librosa.display.waveplot(data, sr=sampling_rate)


# In[8]:


feeling_list=[]
for item in datalist:
    itemarr = item.split('_')
    if item[6:8]=='01':
        feeling_list.append('normal')
    elif item[6:8]=='02':
        feeling_list.append('normal')
    elif item[6:8]=='03':
        feeling_list.append('happy')
    elif item[6:8]=='04':
        feeling_list.append('other')
    elif item[6:8]=='05':
        feeling_list.append('other')
    elif item[6:8]=='06':
        feeling_list.append('other')
    elif item[6:8]=='07':
        feeling_list.append('other')
    elif item[6:8]=='08':
        feeling_list.append('happy')
    elif len(itemarr) == 3:
        emot = itemarr[2].split('.')[0]
        if emot == 'angry':
            feeling_list.append('other')
        elif emot == 'disgust':
            feeling_list.append('other')
        elif emot == 'fear':
            feeling_list.append('other')
        elif emot == 'happy':
            feeling_list.append('happy')
        elif emot == 'neutral':
            feeling_list.append('normal')
        elif emot == 'ps':
            feeling_list.append('happy')
        elif emot == 'sad':
            feeling_list.append('other')
    elif item[:1]=='a':
        feeling_list.append('other')
    elif item[:1]=='d':
        feeling_list.append('other')
    elif item[:1]=='f':
        feeling_list.append('other')
    elif item[:1]=='h':
        feeling_list.append('happy')
    elif item[:1]=='n':
        feeling_list.append('normal')
    elif item[:2]=='sa':
        feeling_list.append('other')
    elif item[:2]=='su':
        feeling_list.append('happy')
#     if item[6:8]=='01':
#         feeling_list.append('neutral')
#     elif item[6:8]=='02':
#         feeling_list.append('calm')
#     elif item[6:8]=='03':
#         feeling_list.append('happy')
#     elif item[6:8]=='04':
#         feeling_list.append('sad')
#     elif item[6:8]=='05':
#         feeling_list.append('angry')
#     elif item[6:8]=='06':
#         feeling_list.append('fearful')
#     elif item[6:8]=='07':
#         feeling_list.append('disgust')
#     elif item[6:8]=='08':
#         feeling_list.append('surprised')
#     elif item[:1]=='a':
#         feeling_list.append('angry')
#     elif item[:1]=='d':
#         feeling_list.append('disgust')
#     elif item[:1]=='f':
#         feeling_list.append('fearful')
#     elif item[:1]=='h':
#         feeling_list.append('happy')
#     elif item[:1]=='n':
#         feeling_list.append('neutral')
#     elif item[:2]=='sa':
#         feeling_list.append('sad')
#     elif item[:2]=='su':
#         feeling_list.append('surprised')


# In[9]:


labels = pd.DataFrame(feeling_list)
labels


# In[217]:


df = pd.DataFrame(columns=['feature'])
bookmark=0
for index,y in enumerate(datalist):
    feature = getEmotionFeatures('data/'+y,2)
    df.loc[bookmark] = [-(feature/100)]
    bookmark=bookmark+1


# In[218]:


df[:5]


# In[219]:


df3 = pd.DataFrame(df['feature'].values.tolist())
newdf = pd.concat([df3,labels], axis=1)
rnewdf = newdf.rename(index=str, columns={"0": "label"})
rnewdf[:5]


# In[220]:


rnewdf = shuffle(newdf)
rnewdf[:10]


# In[221]:


rnewdf = rnewdf.fillna(0)
rnewdf


# In[222]:


newdf1 = np.random.rand(len(rnewdf)) < 0.8
train = rnewdf[newdf1]
test = rnewdf[~newdf1]
train[250:260]
trainfeatures = train.iloc[:, :-1]
trainlabel = train.iloc[:, -1:]
testfeatures = test.iloc[:, :-1]
testlabel = test.iloc[:, -1:]


# In[223]:


X_train = np.array(trainfeatures)
y_train = np.array(trainlabel)
X_test = np.array(testfeatures)
y_test = np.array(testlabel)

lb = LabelEncoder()

y_train = np_utils.to_categorical(lb.fit_transform(y_train))
print(trainlabel[:10])
print(y_train[:10])
y_test = np_utils.to_categorical(lb.fit_transform(y_test))


# In[224]:


print(X_train.shape)
x_traincnn =np.expand_dims(X_train, axis=2)
x_testcnn= np.expand_dims(X_test, axis=2)
print(x_traincnn.shape)


# In[226]:


#cnnhistory=model.fit(x_traincnn, y_train, batch_size=128, epochs=1000, validation_data=(x_testcnn, y_test))
mpepochs = 500
modelBatchSize = 128
earlyPatience = 100
earlystopping_cb = EarlyStopping(monitor='val_loss', verbose=1, patience=earlyPatience, mode='min')
cnnmodel = getCNNModel()
cnnhistory = cnnmodel.fit(x_traincnn, 
                    y_train, 
                    validation_split=0.1, 
                    epochs=mpepochs, 
                    batch_size=modelBatchSize, 
                    callbacks = [earlystopping_cb], 
                    verbose = 1)


# In[227]:


plotTrainingLossAndAccuracy(cnnhistory)
score = model.evaluate(x_testcnn, y_test, verbose=0)
preds = model.predict(x_testcnn, batch_size=32, verbose=1)
print("%s: %.2f%%" % (model.metrics_names[1], score[1]*100))


# In[229]:


model_name = 'Emotion_Voice_Detection_Model.h5'
save_dir = os.path.join(os.getcwd(), 'saved_models')
# Save model and weights
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
print('Saved trained model at %s ' % model_path)


# In[230]:



model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)


# In[20]:


def loadModel():
    from keras.models import model_from_json
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("saved_models/Emotion_Voice_Detection_Model.h5")
    print("Loaded model from disk")

    # evaluate loaded model on test data
    opt = keras.optimizers.Adam(lr=0.0005, decay=1e-6)
    loaded_model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    return loaded_model


# In[232]:


# loading json and creating model
from keras.models import model_from_json
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("saved_models/Emotion_Voice_Detection_Model.h5")
print("Loaded model from disk")
 
# evaluate loaded model on test data
loaded_model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
score = loaded_model.evaluate(x_testcnn, y_test, verbose=0)
preds = loaded_model.predict(x_testcnn, batch_size=32, verbose=1)

print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))


# In[233]:


preds


# In[234]:


preds1=preds.argmax(axis=1)
preds1

abc = preds1.astype(int).flatten()
predictions = (lb.inverse_transform((abc)))

preddf = pd.DataFrame({'predictedvalues': predictions})
preddf[:10]


# In[235]:


actual=y_test.argmax(axis=1)
abc123 = actual.astype(int).flatten()
actualvalues = (lb.inverse_transform((abc123)))
actualdf = pd.DataFrame({'actualvalues': actualvalues})
actualdf[:10]


# In[236]:


finaldf = actualdf.join(preddf)
print(finaldf.groupby('actualvalues').count())
print(finaldf.groupby('predictedvalues').count())
finaldf.to_csv('Predictions.csv', index=False)


# # Test on Live demo

# In[41]:


data, sampling_rate = librosa.load('test2_him.wav')
plt.figure(figsize=(15, 5))
librosa.display.waveplot(data, sr=sampling_rate)
playsound('test2_him.wav')


# In[42]:


padding = pd.DataFrame([0]) 
padding


# In[43]:


sample_duration = 2
tries = 5
result = getEmotionFeatures("test2_him.wav",sample_duration)
padding = pd.DataFrame([0]) 

while(result.shape[0]<313 and tries > 0):
    sample_duration +=0.1
    result = getEmotionFeatures("test2_him.wav",sample_duration)
    tries -=1

featurelive = -(result/100)
livedf2 = featurelive
livedf2= pd.DataFrame(data=livedf2)



#livedf2 = livedf2.stack().to_frame().T
#while(result.shape[0]<313):
#    result[result.shape[0]] = padding
#print(result.shape)
livedf2


# In[44]:


while(livedf2.shape[0]<313):
    livedf2 = livedf2.append(padding,ignore_index = True)
livedf2


# In[45]:


#livedf2= pd.DataFrame(data=livedf2)
#livedf2


# In[46]:


livedf2 = livedf2.stack().to_frame().T
livedf2


# In[47]:


twodim= np.expand_dims(livedf2, axis=2)
twodim.shape


# In[48]:


def getClass(predind):
    if(predind==0):
        return "Happy"
    elif(predind==1):
        return "Normal"
    else:
        return "Other"


# In[49]:


loaded_model = loadModel()
livepreds = loaded_model.predict(twodim, 
                         batch_size=32, 
                         verbose=1)
print(livepreds)
livepreds1=livepreds.argmax(axis=1)
#print(livepreds1)
print("Actual Class and Rating: ",getClass(livepreds1[0]),livepreds[0][livepreds1[0]]*100)
print("Happiness Rating: ",livepreds[0][0]*100)


# In[246]:


'''
lb = LabelEncoder()
livepreds1=livepreds.argmax(axis=1)
liveabc = livepreds1.astype(int).flatten()
livepredictions = (lb.inverse_transform((liveabc)))
livepredictions
'''


# In[ ]:





# # RNN

# In[ ]:




