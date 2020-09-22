# -*- coding: utf-8 -*-
"""
Created on Mon May 18 17:47:31 2020

@author: sinha
"""

from pyspark import SparkContext, SparkConf
import sys

def main():
    
    # Defining the Master on multiple cores of the local system - local[*]
    conf = SparkConf().setMaster('local[*]').setAppName('FindSimilarMovies')
    sc = SparkContext(conf = conf)
    
    # Define the RDD
    movie_data = sc.textFile("file:///Spark course/)
    

if __name__ == '__main__':
    main()    