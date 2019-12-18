# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 18:45:17 2019

@author: sinha
"""
'''
Ref: https://medium.com/the-research-nest/applied-machine-learning-part-3-3fd405842a18
'''

import pandas as pd
import numpy as np
import random
from nltk.corpus import stopwords
import sys
import os
#from textblob import Word

# Function to remove repetitions of letters
import re
def deleteRepetitions(text):
    patterns = re.compile(r"(.)\1{2,}")
    return patterns.sub(r"\1\1", text)

def cleanOriginalData(data):
    # Drop the author columns
    data = data.drop('author', axis = 1)
    
    # Maintain only happiness and sadness values. Change all other emotions to other.
    data.sentiment.replace(['anger','boredom','enthusiasm','empty','fun','relief','surprise','love','hate','neutral','worry'], 
                           ['other','other','other','other','other','other','other','other','other','other','other'], inplace=True)
    
    # Get the count of occurences of happiness, sadness and other labels
    data['sentiment'].value_counts()
    
    # Arrange all values first, and then shuffle the other values. 
    data = data.sort_values(by = ['sentiment'])
    random.shuffle(data['sentiment'] == 'other')
    
    # Reseting the index of the dataframe
    data = data.reset_index()
    
    # Taking only first 160000 values of the dataframe with 
    # happiness, sadness and other all in the same count
    clean_data = data.drop(data.index[9000:34834])
    print( clean_data['sentiment'].value_counts() )
    
    # Shuffling the values in the dataframe and reset the index
    clean_data = clean_data.sample(frac=1).reset_index(drop=True)
    
    # Keep only the sentiment and text columns
    clean_data = clean_data.drop(['index','tweet_id'], axis=1)
    
    # Rearranging the columns in the dataframe
    clean_data = clean_data.reindex(columns=["content","sentiment"])
    
    return clean_data

def preprocessText(clean_data):
    '''
    PREPROCESSING THE TEXT DATA
    1. Making all letters lowercase
    2. Removing Punctuation, Symbols
    3. Removing stop words
    4. Lemmatizing the words
    5. Correct Letter Repetitions
    6. Removing the least frequent words or irrevelant words
    '''
    
    # Convert to lowercase
    clean_data['content'] = clean_data['content'].apply(lambda x: " ".join(x.lower() for x in x.split() ))
    
    # Removing punctuation, symbols
    clean_data['content'] = clean_data['content'].str.replace('[^\w\s]', ' ')
    
    # Using NLTK to remove stopwords
    words = stopwords.words('english')
    clean_data['content'] = clean_data['content'].apply(lambda x:" ".join(x for x in x.split() if x not in words))
    
    # Lemmatizing the words
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    clean_data['content'] = clean_data['content'].apply( lambda x: " ".join( [lemmatizer.lemmatize(w) for w in x.split()] ))
    
    # Correcting Letter Repetitions
    clean_data['content'] = clean_data['content'].apply(lambda x:" ".join(deleteRepetitions(x) for x in x.split()))
    
    # Find the 10,000 rarest words in the data
    word_freq = pd.Series(' '.join(clean_data['content']).split()).value_counts()[-10000:]
    
    # Remove the least frequent words
    word_freq = list(word_freq.index)
    clean_data['content'] = clean_data['content'].apply(lambda x:" ".join(x for x in x.split() if x not in word_freq))
    
    return clean_data

'''
Import the text emotion dataset from Twitter
'''
data = pd.read_csv('train_data/text_emotion.csv')

'''
Clean the original data values
'''
clean_data = cleanOriginalData(data)

'''
Preprocess the text content
'''
clean_data = preprocessText(clean_data)


'''
Extracting the features from the text
1. Encode the labels, happiness - 0, other - 1, sadness - 2
2. Split the data into training and testing set
3. Extract the count vectors - array having the count of appearances of
each word in the tweet. 
'''
# First, encode the sentiment values to 0-happiness, 1-other, 2-sadness
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
labels = encoder.fit_transform(clean_data.sentiment.values)

# Second, split the data into training and testing in 80:20 ratio
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(clean_data.content.values, labels, stratify=labels, random_state=0, test_size=0.2, shuffle=True)

# Third, extracting the count vector parameters
from sklearn.feature_extraction.text import CountVectorizer
count_vectors = CountVectorizer(analyzer='word')
count_vectors.fit(clean_data['content'])

X_train_countvect = count_vectors.transform(X_train)
X_test_countvect = count_vectors.transform(X_test)


'''
Training the ML models to get accuracies
          Linear SVM
'''
from sklearn.metrics import accuracy_score

# Define the Linear SVM model
from sklearn.linear_model import SGDClassifier
SVM = SGDClassifier(loss="modified_huber",alpha=0.001, random_state=5, max_iter=15, tol=None)
SVM.fit(X_train_countvect, y_train)

# Predict the values on the Twitter data
y_pred_svm = SVM.predict(X_test_countvect)
y_pred_prob = SVM.predict_proba(X_test_countvect)
print('\nLSVM using count vectors accuracy %s' % accuracy_score(y_pred_svm, y_test))
''' LSVM Accuracy = 59.78%  - Most Accuracte'''


'''
Save the Model
'''
import pickle
model_path = '../Models/Text/'
model_filename = "SVM.pkl"
with open(model_path + model_filename, 'wb') as file1:
    pickle.dump(SVM, file1)

count_vect_file = "countVectors.pkl"
with open(model_path + count_vect_file, 'wb') as file2:
    pickle.dump(count_vectors, file2)

