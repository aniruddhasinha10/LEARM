# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 00:16:08 2020

@author: sinha
"""

import pandas as pd
import os

pd.options.mode.chained_assignment = None 
session_path = "../Sessions/"

def main():
    session_names = os.listdir(session_path)
    mega = pd.DataFrame()
    mega_avg = pd.DataFrame()
    for session_id in session_names:
        try:
            print ('\n\n------------- Accessing stats files of ' + session_id + ' for compilation -----------')
            processed_file_path = session_path + session_id + "/processed_data/"
            file_suffix = '_stats.csv'
            avg_suffix = '_AvgStats.csv'
            csv = pd.read_csv(processed_file_path + session_id + file_suffix)
            csv_avg = pd.read_csv(processed_file_path + session_id + avg_suffix)
           
            mega = mega.append(csv)
            mega = mega.append(pd.Series(), ignore_index=True)
            mega = mega.append(pd.Series(), ignore_index=True)
            print ('Done appending to the mega csv')
            
            mega_avg = mega_avg.append(csv_avg)
            mega_avg = mega_avg.append(pd.Series(), ignore_index=True)
            mega_avg = mega_avg.append(pd.Series(), ignore_index=True)
            print ('Done appending to the mega avg csv')
        except:
            pass
    mega = mega.drop(mega.columns[0], axis = 1)
    output = pd.DataFrame(mega)
    output.to_csv(session_path + 'mega_stats.csv', index = False)
    print ('\n\nSuccesfully written MEGA csv file')
    
    mega_avg = mega_avg.drop(mega_avg.columns[0], axis = 1)
    output_avg = pd.DataFrame(mega_avg)
    output_avg.to_csv(session_path + 'mega_AvgStats.csv', index = False)
    print ('\n\nSuccesfully written MEGA Avg csv file')

if __name__ == "__main__":
    main()